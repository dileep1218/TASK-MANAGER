"""Business logic layer.

TaskManager sits between the API (or CLI) and the repository. Right
now it mostly delegates, but this is the natural place to add rules
later — e.g. "can't mark a task done if it has unmet sub-tasks" —
without that logic leaking into the database layer or the API routes.
"""

from __future__ import annotations

from typing import Optional

from database import TaskRepository
from task import Task


class TaskManager:
    def __init__(self, repository: Optional[TaskRepository] = None):
        self.repository = repository or TaskRepository()

    def create_task(
        self,
        title: str,
        description: str = "",
        priority: str = "medium",
        due_date: Optional[str] = None,
    ) -> Task:
        task = Task(title=title, description=description, priority=priority, due_date=due_date)
        return self.repository.add(task)

    def get_task(self, task_id: int) -> Task:
        return self.repository.get(task_id)

    def list_tasks(self, status: Optional[str] = None) -> list[Task]:
        return self.repository.list_all(status=status)

    def update_task(self, task_id: int, **fields) -> Task:
        return self.repository.update(task_id, **fields)

    def mark_done(self, task_id: int) -> Task:
        return self.repository.update(task_id, status="done")

    def delete_task(self, task_id: int) -> None:
        self.repository.delete(task_id)
