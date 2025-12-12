"""Async task for sending scheduled tweets.

This module contains the RQ worker task that sends a tweet
at the scheduled time and updates the database status.
"""

import logging
from datetime import datetime, timezone

from result import Err, Ok
from rq import get_current_job
from rq.job import Job

from backend.config import CONFIG
from backend.infrastructure.scheduled_tweet_repository import (
    MongoScheduledTweetRepository,
)
from backend.infrastructure.twitter_client import TwitterClient
from backend.infrastructure.user_repository import MongoUserRepository

logger = logging.getLogger(__name__)


def _log_and_track(message: str, job: Job | None = None) -> None:
    """Log a message and add it to job metadata if job is provided.

    Args:
        message: The message to log
        job: Optional RQ job to update metadata
    """
    logger.info(message)
    if job is not None:
        if "events" not in job.meta:
            job.meta["events"] = []
        job.meta["events"].append(message)
        job.save_meta()  # type: ignore[no-untyped-call]


def execute_send_tweet_job(
    tweet_id: str,
    user_id: str,
    content: str,
) -> dict[str, str]:
    """Job function to send a scheduled tweet.

    This function is designed to be called by RQ workers at the scheduled time.
    It sends the tweet via Twitter API and updates the database status.

    Args:
        tweet_id: The scheduled tweet ID in MongoDB
        user_id: The user ID who scheduled the tweet
        content: The tweet content to send

    Returns:
        Dictionary with status and message
    """
    job = get_current_job()
    if job is not None:
        job.meta["events"] = []
        job.meta["status"] = "running"
        job.meta["tweet_id"] = tweet_id
        job.save_meta()  # type: ignore[no-untyped-call]

    _log_and_track(f"Starting to send scheduled tweet {tweet_id}", job)

    repository = MongoScheduledTweetRepository(CONFIG.mongo_uri, CONFIG.mongo_db_name)
    user_repository = MongoUserRepository(CONFIG.mongo_uri, CONFIG.mongo_db_name)

    # Get user's Twitter OAuth tokens from the database
    _log_and_track(f"Fetching user {user_id} tokens", job)

    user_result = user_repository.find_by_id(user_id)

    tweet_sent_successfully = False
    error_message: str | None = None
    twitter_tweet_id: str | None = None

    match user_result:
        case Ok(user):
            if user.access_token is None:
                error_message = "User has no Twitter access token"
                _log_and_track(error_message, job)
            elif user.provider != "twitter":
                error_message = "User is not authenticated with Twitter"
                _log_and_track(error_message, job)
            else:
                _log_and_track(f"Sending tweet: {content[:50]}...", job)

                # Create Twitter client with user's tokens
                twitter_client = TwitterClient(
                    access_token=user.access_token,
                    refresh_token=user.refresh_token,
                )

                # Attempt to post tweet with automatic token refresh
                post_result = twitter_client.post_tweet_with_retry(content)

                match post_result:
                    case Ok(posted_tweet_id):
                        tweet_sent_successfully = True
                        twitter_tweet_id = posted_tweet_id
                        _log_and_track(
                            f"Tweet sent successfully, Twitter ID: {posted_tweet_id}",
                            job,
                        )

                        # If token was refreshed, update it in the database
                        if twitter_client.access_token != user.access_token:
                            _log_and_track("Updating refreshed tokens in database", job)
                            refresh_result = twitter_client.refresh_access_token()
                            match refresh_result:
                                case Ok(token_result):
                                    user_repository.update_tokens(
                                        user_id,
                                        token_result.access_token,
                                        token_result.refresh_token,
                                        token_result.expires_at,
                                    )
                                case Err(_):
                                    pass  # Token update failed, but tweet was sent

                    case Err(post_error):
                        error_message = post_error
                        _log_and_track(f"Failed to send tweet: {post_error}", job)

        case Err(user_error):
            error_message = f"Failed to fetch user: {user_error}"
            _log_and_track(error_message, job)

    if tweet_sent_successfully:
        _log_and_track("Tweet sent successfully", job)

        # Update status in database
        update_result = repository.update_status(
            tweet_id,
            status="sent",
            sent_at=datetime.now(timezone.utc),
            twitter_tweet_id=twitter_tweet_id,
        )

        match update_result:
            case _:
                pass  # Status updated or error logged

        if job is not None:
            job.meta["status"] = "completed"
            job.meta["twitter_tweet_id"] = twitter_tweet_id
            job.save_meta()  # type: ignore[no-untyped-call]

        return {"status": "sent", "message": "Tweet sent successfully"}
    else:
        _log_and_track(f"Failed to send tweet: {error_message}", job)

        # Update status in database
        repository.update_status(
            tweet_id,
            status="failed",
            error_message=error_message,
        )

        if job is not None:
            job.meta["status"] = "failed"
            job.meta["error"] = error_message
            job.save_meta()  # type: ignore[no-untyped-call]

        return {"status": "failed", "message": error_message or "Unknown error"}
