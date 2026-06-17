"""Command-line entry point for the Task Manager.

This file is intentionally thin: all real logic lives in TaskManager,
TaskRepository, and Task. main.py just wires up a simple text menu on
top of that, so the same business logic could later be reused by the
FastAPI layer (or a different UI) without duplicating anything here.
"""

from __future__ import annotations

from exceptions import InvalidTaskDataError, TaskManagerError, TaskNotFoundError
from task_manager import TaskManager

MENU = """
==== Task Manager ====
1. Add task
2. List all tasks
3. List tasks by status
4. Update task
5. Mark task as done
6. Delete task
0. Exit
"""


def print_task(task) -> None:
    print(
        f"[{task.id}] {task.title} "
        f"(priority={task.priority}, status={task.status}, due={task.due_date or '—'})"
    )
    if task.description:
        print(f"    {task.description}")


def add_task(manager: TaskManager) -> None:
    title = input("Title: ").strip()
    description = input("Description (optional): ").strip()
    priority = input("Priority [low/medium/high] (default medium): ").strip() or "medium"
    due_date = input("Due date YYYY-MM-DD (optional): ").strip() or None

    task = manager.create_task(title=title, description=description, priority=priority, due_date=due_date)
    print(f"Created task #{task.id}.")


def list_tasks(manager: TaskManager, status: str | None = None) -> None:
    tasks = manager.list_tasks(status=status)
    if not tasks:
        print("No tasks found.")
        return
    for task in tasks:
        print_task(task)


def update_task(manager: TaskManager) -> None:
    task_id = int(input("Task id to update: ").strip())
    print("Leave a field blank to keep its current value.")
    fields = {}
    for field in ("title", "description", "priority", "status", "due_date"):
        value = input(f"New {field}: ").strip()
        if value:
            fields[field] = value
    updated = manager.update_task(task_id, **fields)
    print("Updated:")
    print_task(updated)


def mark_done(manager: TaskManager) -> None:
    task_id = int(input("Task id to mark done: ").strip())
    task = manager.mark_done(task_id)
    print(f"Task #{task.id} marked as done.")


def delete_task(manager: TaskManager) -> None:
    task_id = int(input("Task id to delete: ").strip())
    manager.delete_task(task_id)
    print(f"Task #{task_id} deleted.")


def main() -> None:
    manager = TaskManager()

    actions = {
        "1": add_task,
        "4": update_task,
        "5": mark_done,
        "6": delete_task,
    }

    while True:
        print(MENU)
        choice = input("Choose an option: ").strip()

        try:
            if choice == "0":
                print("Goodbye.")
                break
            elif choice == "2":
                list_tasks(manager)
            elif choice == "3":
                status = input("Status to filter by [pending/done]: ").strip()
                list_tasks(manager, status=status)
            elif choice in actions:
                actions[choice](manager)
            else:
                print("Invalid option, try again.")
        except (InvalidTaskDataError, TaskNotFoundError) as exc:
            print(f"Error: {exc}")
        except TaskManagerError as exc:
            print(f"Unexpected error: {exc}")
        except ValueError:
            print("Please enter a valid number for task id.")


if __name__ == "__main__":
    main()
