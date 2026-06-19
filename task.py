"""Task domain model.

A Task is a plain data holder with validation logic attached, so the
rest of the codebase can trust that any Task object in memory is
already valid — invalid data is rejected at construction time rather
than discovered later when it's saved or displayed.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from typing import Optional

from exceptions import InvalidTaskDataError

VALID_PRIORITIES = {"low", "medium", "high"}
VALID_STATUSES = {"pending", "done"}


@dataclass
class Task:
    title: str
    description: str = ""
    priority: str = "medium"
    status: str = "pending"
    due_date: Optional[str] = None  # stored as ISO format string, e.g. "2026-06-30"
    id: Optional[int] = None
    created_at: str = field(default_factory=lambda: datetime.now(timezone.utc).isoformat())

    def __post_init__(self) -> None:
        self.title = self.title.strip()
        self.priority = self.priority.lower().strip()
        self.status = self.status.lower().strip()
        self._validate()

    def _validate(self) -> None:
        if not self.title:
            raise InvalidTaskDataError("Task title cannot be empty.")

        if self.priority not in VALID_PRIORITIES:
            raise InvalidTaskDataError(
                f"Invalid priority '{self.priority}'. Must be one of {sorted(VALID_PRIORITIES)}."
            )

        if self.status not in VALID_STATUSES:
            raise InvalidTaskDataError(
                f"Invalid status '{self.status}'. Must be one of {sorted(VALID_STATUSES)}."
            )

        if self.due_date:
            try:
                date.fromisoformat(self.due_date)
            except ValueError as exc:
                raise InvalidTaskDataError(
                    f"Invalid due_date '{self.due_date}'. Expected format YYYY-MM-DD."
                ) from exc

    def mark_done(self) -> None:
        self.status = "done"

    def to_dict(self) -> dict:
        return {
            "id": self.id,
            "title": self.title,
            "description": self.description,
            "priority": self.priority,
            "status": self.status,
            "due_date": self.due_date,
            "created_at": self.created_at,
        }

    @classmethod
    def from_row(cls, row: tuple) -> "Task":
        """Build a Task from a sqlite3 row tuple in the order columns are selected."""
        (task_id, title, description, priority, status, due_date, created_at) = row
        return cls(
            id=task_id,
            title=title,
            description=description,
            priority=priority,
            status=status,
            due_date=due_date,
            created_at=created_at,
        )
