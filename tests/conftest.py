"""Shared pytest fixtures.

Both test_task_manager.py and test_api.py need an isolated, throwaway
database for each test — never the real tasks.db — so tests can run
repeatedly without leftover data from a previous run affecting results.
"""

import os

import pytest

from database import TaskRepository
from task_manager import TaskManager

TEST_DB_PATH = "test_tasks_temp.db"


@pytest.fixture
def manager():
    """A TaskManager backed by a fresh, temporary SQLite file."""
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)

    repo = TaskRepository(db_path=TEST_DB_PATH)
    yield TaskManager(repository=repo)

    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)
