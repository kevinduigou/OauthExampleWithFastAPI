"""MongoDB repository for scheduled tweets.

This infrastructure layer component handles:
- CRUD operations for scheduled tweets
- Querying scheduled tweets by user
- Updating tweet status
"""

from datetime import datetime, timezone
from typing import Any, final

from bson import ObjectId
from pymongo import MongoClient
from pymongo.collection import Collection
from result import Err, Ok, Result

from backend.domain.scheduled_tweet import ScheduledTweet


@final
class MongoScheduledTweetRepository:
    """Repository for managing scheduled tweets in MongoDB."""

    __slots__ = ("_client", "_collection")

    def __init__(self, uri: str, db_name: str) -> None:
        """Initialize the repository.

        Args:
            uri: MongoDB connection URI
            db_name: Database name
        """
        self._client: MongoClient[Any] = MongoClient(uri)
        database = self._client[db_name]
        self._collection: Collection[Any] = database["scheduled_tweets"]

    def create(self, tweet: ScheduledTweet) -> Result[str, str]:
        """Create a new scheduled tweet.

        Args:
            tweet: The scheduled tweet to create

        Returns:
            Ok(identifier) if successful, Err(error_message) if failed
        """
        try:
            document: dict[str, object] = {
                "user_id": tweet.user_id,
                "content": tweet.content,
                "scheduled_at": tweet.scheduled_at,
                "status": tweet.status,
                "job_id": tweet.job_id,
                "created_at": tweet.created_at or datetime.now(timezone.utc),
                "sent_at": tweet.sent_at,
                "error_message": tweet.error_message,
            }
            result = self._collection.insert_one(document)
            return Ok(str(result.inserted_id))
        except Exception as exc:  # noqa: BLE001
            return Err(str(exc))

    def _build_tweet(self, document: dict[str, object]) -> ScheduledTweet:
        """Build a ScheduledTweet from a MongoDB document.

        Args:
            document: MongoDB document

        Returns:
            ScheduledTweet entity
        """
        scheduled_at = document.get("scheduled_at")
        created_at = document.get("created_at")
        sent_at = document.get("sent_at")

        return ScheduledTweet(
            user_id=str(document.get("user_id", "")),
            content=str(document.get("content", "")),
            scheduled_at=scheduled_at
            if isinstance(scheduled_at, datetime)
            else datetime.now(timezone.utc),
            status=str(document.get("status", "pending")),
            job_id=str(document.get("job_id")) if document.get("job_id") else None,
            identifier=str(document.get("_id", "")),
            created_at=created_at if isinstance(created_at, datetime) else None,
            sent_at=sent_at if isinstance(sent_at, datetime) else None,
            error_message=str(document.get("error_message"))
            if document.get("error_message")
            else None,
        )

    def find_by_id(self, tweet_id: str) -> Result[ScheduledTweet, str]:
        """Find a scheduled tweet by ID.

        Args:
            tweet_id: The tweet ID to find

        Returns:
            Ok(ScheduledTweet) if found, Err(error_message) if not found
        """
        try:
            document = self._collection.find_one({"_id": ObjectId(tweet_id)})
            if document is None:
                return Err("Scheduled tweet not found")
            return Ok(self._build_tweet(document))
        except Exception as exc:  # noqa: BLE001
            return Err(str(exc))

    def find_by_user(self, user_id: str) -> Result[tuple[ScheduledTweet, ...], str]:
        """Find all scheduled tweets for a user.

        Args:
            user_id: The user ID to find tweets for

        Returns:
            Ok(tuple of ScheduledTweet) if successful, Err(error_message) if failed
        """
        try:
            documents = self._collection.find({"user_id": user_id}).sort(
                "scheduled_at", 1
            )
            tweets = tuple(self._build_tweet(doc) for doc in documents)
            return Ok(tweets)
        except Exception as exc:  # noqa: BLE001
            return Err(str(exc))

    def update_status(
        self,
        tweet_id: str,
        status: str,
        sent_at: datetime | None = None,
        error_message: str | None = None,
        twitter_tweet_id: str | None = None,
    ) -> Result[None, str]:
        """Update the status of a scheduled tweet.

        Args:
            tweet_id: The tweet ID to update
            status: New status value
            sent_at: When the tweet was sent (if applicable)
            error_message: Error message (if applicable)
            twitter_tweet_id: The Twitter API tweet ID (if applicable)

        Returns:
            Ok(None) if successful, Err(error_message) if failed
        """
        try:
            updates: dict[str, object] = {"status": status}
            if sent_at is not None:
                updates["sent_at"] = sent_at
            if error_message is not None:
                updates["error_message"] = error_message
            if twitter_tweet_id is not None:
                updates["twitter_tweet_id"] = twitter_tweet_id

            result = self._collection.update_one(
                {"_id": ObjectId(tweet_id)},
                {"$set": updates},
            )
            if result.matched_count == 0:
                return Err("Scheduled tweet not found")
            return Ok(None)
        except Exception as exc:  # noqa: BLE001
            return Err(str(exc))

    def update_job_id(self, tweet_id: str, job_id: str) -> Result[None, str]:
        """Update the job ID of a scheduled tweet.

        Args:
            tweet_id: The tweet ID to update
            job_id: The RQ job ID

        Returns:
            Ok(None) if successful, Err(error_message) if failed
        """
        try:
            result = self._collection.update_one(
                {"_id": ObjectId(tweet_id)},
                {"$set": {"job_id": job_id}},
            )
            if result.matched_count == 0:
                return Err("Scheduled tweet not found")
            return Ok(None)
        except Exception as exc:  # noqa: BLE001
            return Err(str(exc))

    def delete(self, tweet_id: str) -> Result[None, str]:
        """Delete a scheduled tweet.

        Args:
            tweet_id: The tweet ID to delete

        Returns:
            Ok(None) if successful, Err(error_message) if failed
        """
        try:
            result = self._collection.delete_one({"_id": ObjectId(tweet_id)})
            if result.deleted_count == 0:
                return Err("Scheduled tweet not found")
            return Ok(None)
        except Exception as exc:  # noqa: BLE001
            return Err(str(exc))
