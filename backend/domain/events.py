"""Domain events - Immutable event objects representing domain occurrences.

Events are immutable value objects that represent something that happened
in the domain. They are used to communicate between layers and components.
"""

from dataclasses import dataclass
from typing import final


@final
@dataclass(frozen=True, slots=True)
class TaskCompleted:
    """Event representing the completion of a long-running task.

    Attributes:
        items_processed: Number of items successfully processed
        message: Human-readable completion message
    """

    items_processed: int
    message: str
