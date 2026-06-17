
from __future__ import annotations

import sqlite3
from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Optional

from exceptions import TaskNotFoundError
from task import Task

DEFAULT_DB_PATH = Path(__file__).parent / "tasks.db"

SCHEMA = """
CREATE TABLE IF NOT EXISTS tasks (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    title TEXT NOT NULL,
    description TEXT DEFAULT '',
    priority TEXT NOT NULL DEFAULT 'medium',
    status TEXT NOT NULL DEFAULT 'pending',
    due_date TEXT,
    created_at TEXT NOT NULL
);
"""


class TaskRepository:
    """Handles all database access for Task objects."""

    def __init__(self, db_path: Path | str = DEFAULT_DB_PATH):
        self.db_path = str(db_path)
        self._init_schema()

    @contextmanager
    def _connect(self) -> Iterator[sqlite3.Connection]:
        conn = sqlite3.connect(self.db_path)
        try:
            yield conn
            conn.commit()
        finally:
            conn.close()

    def _init_schema(self) -> None:
        with self._connect() as conn:
            conn.execute(SCHEMA)

    def add(self, task: Task) -> Task:
        with self._connect() as conn:
            cursor = conn.execute(
                """
                INSERT INTO tasks (title, description, priority, status, due_date, created_at)
                VALUES (?, ?, ?, ?, ?, ?)
                """,
                (
                    task.title,
                    task.description,
                    task.priority,
                    task.status,
                    task.due_date,
                    task.created_at,
                ),
            )
            task.id = cursor.lastrowid
        return task

    def get(self, task_id: int) -> Task:
        with self._connect() as conn:
            row = conn.execute(
                """
                SELECT id, title, description, priority, status, due_date, created_at
                FROM tasks WHERE id = ?
                """,
                (task_id,),
            ).fetchone()
        if row is None:
            raise TaskNotFoundError(task_id)
        return Task.from_row(row)

    def list_all(self, status: Optional[str] = None) -> list[Task]:
        query = """
            SELECT id, title, description, priority, status, due_date, created_at
            FROM tasks
        """
        params: tuple = ()
        if status:
            query += " WHERE status = ?"
            params = (status.lower().strip(),)
        query += " ORDER BY created_at DESC"

        with self._connect() as conn:
            rows = conn.execute(query, params).fetchall()
        return [Task.from_row(row) for row in rows]

    def update(self, task_id: int, **fields) -> Task:
        existing = self.get(task_id)  # raises TaskNotFoundError if missing

        updated = Task(
            id=existing.id,
            title=fields.get("title", existing.title),
            description=fields.get("description", existing.description),
            priority=fields.get("priority", existing.priority),
            status=fields.get("status", existing.status),
            due_date=fields.get("due_date", existing.due_date),
            created_at=existing.created_at,
        )

        with self._connect() as conn:
            conn.execute(
                """
                UPDATE tasks
                SET title = ?, description = ?, priority = ?, status = ?, due_date = ?
                WHERE id = ?
                """,
                (
                    updated.title,
                    updated.description,
                    updated.priority,
                    updated.status,
                    updated.due_date,
                    task_id,
                ),
            )
        return updated

    def delete(self, task_id: int) -> None:
        self.get(task_id)  # raises TaskNotFoundError if missing, before attempting delete
        with self._connect() as conn:
            conn.execute("DELETE FROM tasks WHERE id = ?", (task_id,))
