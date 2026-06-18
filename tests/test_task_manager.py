"""Unit tests for TaskManager (and indirectly, Task + TaskRepository).

These tests exercise the business logic layer directly, without going
through HTTP — fast, and they pin down behavior independent of any
API framework choice.
"""

import pytest

from exceptions import InvalidTaskDataError, TaskNotFoundError


class TestCreateTask:
    def test_create_task_with_defaults(self, manager):
        task = manager.create_task(title="Write report")
        assert task.id is not None
        assert task.title == "Write report"
        assert task.priority == "medium"
        assert task.status == "pending"

    def test_create_task_with_all_fields(self, manager):
        task = manager.create_task(
            title="Submit taxes",
            description="Before the deadline",
            priority="high",
            due_date="2026-06-30",
        )
        assert task.priority == "high"
        assert task.due_date == "2026-06-30"

    def test_create_task_strips_whitespace_from_title(self, manager):
        task = manager.create_task(title="   Buy milk   ")
        assert task.title == "Buy milk"

    def test_create_task_rejects_empty_title(self, manager):
        with pytest.raises(InvalidTaskDataError):
            manager.create_task(title="   ")

    def test_create_task_rejects_invalid_priority(self, manager):
        with pytest.raises(InvalidTaskDataError):
            manager.create_task(title="Test", priority="urgent")

    def test_create_task_rejects_invalid_due_date_format(self, manager):
        with pytest.raises(InvalidTaskDataError):
            manager.create_task(title="Test", due_date="30-06-2026")


class TestGetTask:
    def test_get_existing_task(self, manager):
        created = manager.create_task(title="Find me")
        fetched = manager.get_task(created.id)
        assert fetched.id == created.id
        assert fetched.title == "Find me"

    def test_get_nonexistent_task_raises(self, manager):
        with pytest.raises(TaskNotFoundError):
            manager.get_task(9999)


class TestListTasks:
    def test_list_returns_all_tasks(self, manager):
        manager.create_task(title="Task A")
        manager.create_task(title="Task B")
        tasks = manager.list_tasks()
        assert len(tasks) == 2

    def test_list_empty_when_no_tasks(self, manager):
        assert manager.list_tasks() == []

    def test_list_filtered_by_status(self, manager):
        t1 = manager.create_task(title="Pending one")
        t2 = manager.create_task(title="Done one")
        manager.mark_done(t2.id)

        pending = manager.list_tasks(status="pending")
        done = manager.list_tasks(status="done")

        assert [t.id for t in pending] == [t1.id]
        assert [t.id for t in done] == [t2.id]


class TestUpdateTask:
    def test_update_changes_only_given_fields(self, manager):
        task = manager.create_task(title="Original", priority="low")
        updated = manager.update_task(task.id, priority="high")

        assert updated.title == "Original"  # unchanged
        assert updated.priority == "high"  # changed

    def test_update_nonexistent_task_raises(self, manager):
        with pytest.raises(TaskNotFoundError):
            manager.update_task(9999, title="Doesn't matter")

    def test_update_with_invalid_priority_raises(self, manager):
        task = manager.create_task(title="Test")
        with pytest.raises(InvalidTaskDataError):
            manager.update_task(task.id, priority="urgent")


class TestMarkDone:
    def test_mark_done_changes_status(self, manager):
        task = manager.create_task(title="Finish this")
        updated = manager.mark_done(task.id)
        assert updated.status == "done"

    def test_mark_done_nonexistent_task_raises(self, manager):
        with pytest.raises(TaskNotFoundError):
            manager.mark_done(9999)


class TestDeleteTask:
    def test_delete_removes_task(self, manager):
        task = manager.create_task(title="Temporary")
        manager.delete_task(task.id)
        with pytest.raises(TaskNotFoundError):
            manager.get_task(task.id)

    def test_delete_nonexistent_task_raises(self, manager):
        with pytest.raises(TaskNotFoundError):
            manager.delete_task(9999)
