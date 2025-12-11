"""Example long-running task with progress tracking.

This module demonstrates how to create a long-running async job that:
- Updates job metadata for progress tracking
- Communicates with the frontend via job metadata
- Follows clean architecture principles
- Uses Result type for error handling
"""

import logging
import time
from typing import Any

from result import Err, Ok, Result
from rq import get_current_job
from rq.job import Job

from backend.domain.events import TaskCompleted

logger = logging.getLogger(__name__)


def _log_and_track(message: str, job: Job | None = None, *args: Any) -> None:
    """Log a message and add it to job metadata if job is provided.

    Args:
        message: The message to log (can include format placeholders)
        job: Optional RQ job to update metadata
        *args: Arguments for message formatting
    """
    logger.info(message, *args)
    if job is not None:
        # Format the message with args for metadata
        formatted_message = message % args if args else message
        job.meta["events"].append(formatted_message)
        job.meta["progress"] = job.meta.get("progress", 0)
        job.save_meta()  # type: ignore[no-untyped-call]


class ExampleLongTaskUseCase:
    """Use case for a long-running task with progress tracking.

    This use case simulates processing multiple items and demonstrates
    how to properly track progress for frontend monitoring.
    """

    def execute(
        self,
        total_items: int = 100,
        job: Job | None = None,
    ) -> Result[TaskCompleted, str]:
        """Execute the long-running task.

        Args:
            total_items: Number of items to process
            job: Optional RQ job for progress tracking

        Returns:
            Ok(TaskCompleted) if successful, Err(str) with error message if failed
        """
        if total_items <= 0:
            return Err("total_items must be greater than 0")

        _log_and_track("Starting long-running task with %d items", job, total_items)

        # Initialize progress tracking
        if job is not None:
            job.meta["progress"] = 0
            job.meta["total"] = total_items
            job.meta["current_item"] = 0
            job.save_meta()  # type: ignore[no-untyped-call]

        processed_count = 0

        # Simulate processing items
        for item_index in range(total_items):
            # Simulate work (100-150ms per item)
            time.sleep(0.15)

            # Update progress
            processed_count += 1
            progress_percentage = int((processed_count / total_items) * 100)

            if job is not None:
                job.meta["progress"] = progress_percentage
                job.meta["current_item"] = item_index + 1
                job.save_meta()  # type: ignore[no-untyped-call]

            # Log progress at milestones
            if processed_count % 25 == 0:
                _log_and_track(
                    "Milestone reached: %d items processed",
                    job,
                    processed_count,
                )

            # Log checkpoint at 50% intervals
            if processed_count % 50 == 0 or processed_count == total_items:
                _log_and_track(
                    "Checkpoint: %d/%d complete (%d%%)",
                    job,
                    processed_count,
                    total_items,
                    progress_percentage,
                )

        _log_and_track("Task completed successfully", job)

        return Ok(
            TaskCompleted(
                items_processed=processed_count,
                message=f"Successfully processed {processed_count} items",
            )
        )


def execute_example_long_task_job(
    total_items: int = 100,
) -> TaskCompleted:
    """Job function to execute the example long-running task.

    This function is designed to be called by RQ workers.
    It initializes job metadata and delegates to the use case.

    Args:
        total_items: Number of items to process

    Returns:
        TaskCompleted with job result information
    """
    # Get current job for tracking progress
    job = get_current_job()
    if job is not None:
        job.meta["events"] = []
        job.meta["status"] = "running"
        job.save_meta()  # type: ignore[no-untyped-call]

    logger.info("Starting example long task job")
    logger.info("Total items: %d", total_items)

    if job is not None:
        job.meta["events"].append("Job started")
        job.save_meta()  # type: ignore[no-untyped-call]

    use_case = ExampleLongTaskUseCase()

    result = use_case.execute(total_items=total_items, job=job)

    match result:
        case Ok(event):
            logger.info(
                "Job completed successfully, processed %d items",
                event.items_processed,
            )
            if job is not None:
                job.meta["events"].append(
                    f"Successfully processed {event.items_processed} items"
                )
                job.meta["status"] = "completed"
                job.save_meta()  # type: ignore[no-untyped-call]
            return TaskCompleted(
                items_processed=event.items_processed,
                message=event.message,
            )
        case Err(error):
            logger.error("Job failed: %s", error)
            if job is not None:
                job.meta["events"].append(f"Job failed: {error}")
                job.meta["status"] = "failed"
                job.save_meta()  # type: ignore[no-untyped-call]
            return TaskCompleted(
                items_processed=0,
                message=f"Job failed: {error}",
            )
