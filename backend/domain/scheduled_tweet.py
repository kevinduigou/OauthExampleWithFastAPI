"""Domain model for scheduled tweets.

This module contains the ScheduledTweet entity which represents
a tweet that is scheduled to be sent at a specific date and time.
"""

from dataclasses import dataclass
from datetime import datetime
from typing import final


@final
@dataclass(slots=True)
class ScheduledTweet:
    """Entity representing a scheduled tweet.

    Attributes:
        user_id: The ID of the user who scheduled the tweet
        content: The text content of the tweet
        scheduled_at: The exact datetime when the tweet should be sent
        status: Current status (pending, sent, failed, cancelled)
        job_id: The RQ job ID for the scheduled task
        identifier: MongoDB document ID
        created_at: When the scheduled tweet was created
        sent_at: When the tweet was actually sent (if sent)
        error_message: Error message if sending failed
    """

    user_id: str
    content: str
    scheduled_at: datetime
    status: str = "pending"
    job_id: str | None = None
    identifier: str | None = None
    created_at: datetime | None = None
    sent_at: datetime | None = None
    error_message: str | None = None
