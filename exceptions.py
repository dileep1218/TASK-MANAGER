class TaskManagerError(Exception):
    """Base class for all Task Manager specific errors."""


class TaskNotFoundError(TaskManagerError):
    """Raised when a task with the given id does not exist."""

    def __init__(self, task_id: int):
        self.task_id = task_id
        super().__init__(f"Task with id {task_id} was not found.")


class InvalidTaskDataError(TaskManagerError):
    """Raised when task data fails validation (e.g. empty title, bad priority)."""
