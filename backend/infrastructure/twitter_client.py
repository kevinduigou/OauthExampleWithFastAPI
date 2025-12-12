"""Twitter API client for posting tweets.

This module provides a client for interacting with the Twitter API v2
to post tweets on behalf of authenticated users.
"""

import os
from dataclasses import dataclass
from datetime import datetime, timedelta, timezone
from typing import final

import httpx
from result import Err, Ok, Result


@final
@dataclass(frozen=True, slots=True)
class TokenRefreshResult:
    """Result of a successful token refresh operation."""

    access_token: str
    refresh_token: str
    expires_at: datetime


@final
class TwitterClient:
    """Client for Twitter API v2 operations."""

    __slots__ = (
        "_access_token",
        "_refresh_token",
        "_client_id",
        "_client_secret",
    )

    TWITTER_API_BASE = "https://api.twitter.com/2"
    TWITTER_TOKEN_URL = "https://api.twitter.com/2/oauth2/token"

    def __init__(
        self,
        access_token: str,
        refresh_token: str | None = None,
        client_id: str | None = None,
        client_secret: str | None = None,
    ) -> None:
        """Initialize the Twitter client.

        Args:
            access_token: The user's OAuth 2.0 access token
            refresh_token: The user's OAuth 2.0 refresh token (optional)
            client_id: Twitter app client ID (defaults to env var)
            client_secret: Twitter app client secret (defaults to env var)
        """
        self._access_token = access_token
        self._refresh_token = refresh_token
        self._client_id = client_id or os.getenv("TWITTER_CLIENT_ID", "")
        self._client_secret = client_secret or os.getenv("TWITTER_CLIENT_SECRET", "")

    @property
    def access_token(self) -> str:
        """Get the current access token."""
        return self._access_token

    def refresh_access_token(self) -> Result[TokenRefreshResult, str]:
        """Refresh the access token using the refresh token.

        Returns:
            Result containing TokenRefreshResult with new tokens and expiry
            or an error message
        """
        if not self._refresh_token:
            return Err("No refresh token available")

        if not self._client_id or not self._client_secret:
            return Err("Twitter client credentials not configured")

        try:
            with httpx.Client() as client:
                response = client.post(
                    self.TWITTER_TOKEN_URL,
                    data={
                        "grant_type": "refresh_token",
                        "refresh_token": self._refresh_token,
                        "client_id": self._client_id,
                    },
                    auth=(self._client_id, self._client_secret),
                    headers={"Content-Type": "application/x-www-form-urlencoded"},
                )

                if response.status_code != 200:
                    error_data = response.json()
                    error_msg = error_data.get(
                        "error_description", error_data.get("error", "Unknown error")
                    )
                    return Err(f"Token refresh failed: {error_msg}")

                token_data = response.json()
                new_access_token = token_data.get("access_token", "")
                new_refresh_token = token_data.get("refresh_token", self._refresh_token)
                expires_in = token_data.get("expires_in", 7200)

                # Update internal tokens
                self._access_token = new_access_token
                self._refresh_token = new_refresh_token

                expires_at = datetime.now(timezone.utc).replace(
                    microsecond=0
                ) + timedelta(seconds=expires_in)

                return Ok(
                    TokenRefreshResult(
                        access_token=new_access_token,
                        refresh_token=new_refresh_token,
                        expires_at=expires_at,
                    )
                )

        except httpx.RequestError as exc:
            return Err(f"Network error during token refresh: {exc}")
        except Exception as exc:  # noqa: BLE001
            return Err(f"Unexpected error during token refresh: {exc}")

    def post_tweet(self, content: str) -> Result[str, str]:
        """Post a tweet using the Twitter API v2.

        Args:
            content: The tweet text content (max 280 characters)

        Returns:
            Result containing the tweet ID on success, or an error message
        """
        if not content:
            return Err("Tweet content cannot be empty")

        if len(content) > 280:
            return Err(f"Tweet content exceeds 280 characters: {len(content)}")

        try:
            with httpx.Client() as client:
                response = client.post(
                    f"{self.TWITTER_API_BASE}/tweets",
                    json={"text": content},
                    headers={
                        "Authorization": f"Bearer {self._access_token}",
                        "Content-Type": "application/json",
                    },
                )

                if response.status_code == 401:
                    return Err("Unauthorized: Access token may be expired")

                if response.status_code == 403:
                    error_data = response.json()
                    detail = error_data.get("detail", "Forbidden")
                    return Err(f"Forbidden: {detail}")

                if response.status_code not in (200, 201):
                    error_data = response.json()
                    error_msg = error_data.get("detail", str(error_data))
                    return Err(
                        f"Twitter API error ({response.status_code}): {error_msg}"
                    )

                tweet_data = response.json()
                tweet_id = tweet_data.get("data", {}).get("id", "")

                if not tweet_id:
                    return Err("Tweet created but no ID returned")

                return Ok(tweet_id)

        except httpx.RequestError as exc:
            return Err(f"Network error posting tweet: {exc}")
        except Exception as exc:  # noqa: BLE001
            return Err(f"Unexpected error posting tweet: {exc}")

    def post_tweet_with_retry(self, content: str) -> Result[str, str]:
        """Post a tweet, refreshing the token if needed.

        This method attempts to post a tweet and automatically refreshes
        the access token if the initial request fails with a 401 error.

        Args:
            content: The tweet text content

        Returns:
            Result containing the tweet ID on success, or an error message
        """
        # First attempt
        result = self.post_tweet(content)

        match result:
            case Ok(tweet_id):
                return Ok(tweet_id)
            case Err(error):
                # Check if it's an authorization error
                if "Unauthorized" in error or "expired" in error.lower():
                    # Try to refresh the token
                    refresh_result = self.refresh_access_token()
                    match refresh_result:
                        case Ok(_):
                            # Retry with new token
                            return self.post_tweet(content)
                        case Err(refresh_error):
                            return Err(f"Token refresh failed: {refresh_error}")
                return Err(error)
