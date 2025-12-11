"""RQ Client for managing async job queues.

This infrastructure layer component handles:
- Job enqueueing with Redis RQ
- Job status monitoring
- Job metadata retrieval
- Job cancellation
"""

import os
from typing import Any

import redis
from result import Err, Ok, Result
from rq import Queue
from rq.job import Job


class RQClient:
    """Client for Redis Queue (RQ) job management.

    This class provides a clean interface for enqueueing and monitoring
    long-running jobs using Redis as the backend.
    """

    def __init__(self, redis_url: str | None = None):
        """Initialize the RQ client.

        Args:
            redis_url: Redis connection URL (default: from REDIS_URL env var or localhost)
        """
        if redis_url is None:
            redis_url = os.getenv("REDIS_URL", "redis://localhost:6379/0")

        try:
            self._redis_connection = redis.from_url(redis_url)  # type: ignore[no-untyped-call]
            self._queue = Queue(connection=self._redis_connection)
        except Exception as error:
            raise RuntimeError(f"Failed to connect to Redis: {error}") from error

    def enqueue_job(
        self,
        function_path: str,
        *args: Any,
        job_timeout: int = 3600,
        **kwargs: Any,
    ) -> Result[str, str]:
        """Enqueue a job for async execution.

        Args:
            function_path: Full path to the function (e.g., 'module.function')
            *args: Positional arguments to pass to the function
            job_timeout: Job timeout in seconds (default: 1 hour)
            **kwargs: Keyword arguments to pass to the function

        Returns:
            Ok(job_id) if successful, Err(error_message) if failed
        """
        try:
            job = self._queue.enqueue(
                function_path,
                *args,
                job_timeout=job_timeout,
                **kwargs,
            )
            return Ok(job.id)
        except Exception as error:
            return Err(f"Failed to enqueue job: {error}")

    def get_job_status(self, job_id: str) -> Result[str, str]:
        """Get the current status of a job.

        Args:
            job_id: The job ID to check

        Returns:
            Ok(status) with status string, Err(error_message) if failed
            Possible statuses: 'queued', 'started', 'finished', 'failed', 'canceled'
        """
        try:
            job = Job.fetch(job_id, connection=self._redis_connection)
            return Ok(job.get_status())
        except Exception as error:
            return Err(f"Failed to get job status: {error}")

    def get_job_meta(self, job_id: str) -> Result[dict[str, Any], str]:
        """Get the metadata of a job.

        Args:
            job_id: The job ID to get metadata for

        Returns:
            Ok(metadata_dict) if successful, Err(error_message) if failed
        """
        try:
            job = Job.fetch(job_id, connection=self._redis_connection)
            return Ok(job.meta)
        except Exception as error:
            return Err(f"Failed to get job metadata: {error}")

    def cancel_job(self, job_id: str) -> Result[None, str]:
        """Cancel a running or queued job.

        Args:
            job_id: The job ID to cancel

        Returns:
            Ok(None) if successful, Err(error_message) if failed
        """
        try:
            job = Job.fetch(job_id, connection=self._redis_connection)
            job.cancel()
            return Ok(None)
        except Exception as error:
            return Err(f"Failed to cancel job: {error}")

    def get_job_result(self, job_id: str) -> Result[Any, str]:
        """Get the result of a completed job.

        Args:
            job_id: The job ID to get the result for

        Returns:
            Ok(result) if successful, Err(error_message) if failed
        """
        try:
            job = Job.fetch(job_id, connection=self._redis_connection)
            if job.is_finished:
                return Ok(job.result)
            return Err(f"Job is not finished yet (status: {job.get_status()})")
        except Exception as error:
            return Err(f"Failed to get job result: {error}")
