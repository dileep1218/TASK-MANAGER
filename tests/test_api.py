"""Integration tests for the FastAPI endpoints in app.py.

These go through the real HTTP layer (via TestClient) rather than
calling TaskManager directly, so they catch issues unit tests can't —
wrong status codes, broken request/response schemas, route typos.

The app's get_manager dependency is overridden per-test to point at a
temporary database, so these tests never touch the real tasks.db and
don't interfere with each other.
"""

import os

import pytest
from fastapi.testclient import TestClient

from app import app, get_manager
from database import TaskRepository
from task_manager import TaskManager

TEST_DB_PATH = "test_api_temp.db"


@pytest.fixture
def client():
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)

    test_manager = TaskManager(repository=TaskRepository(db_path=TEST_DB_PATH))
    app.dependency_overrides[get_manager] = lambda: test_manager

    with TestClient(app) as test_client:
        yield test_client

    app.dependency_overrides.clear()
    if os.path.exists(TEST_DB_PATH):
        os.remove(TEST_DB_PATH)


def test_read_root(client):
    response = client.get("/")
    assert response.status_code == 200


def test_create_task_returns_201(client):
    response = client.post("/tasks", json={"title": "Write report", "priority": "high"})
    assert response.status_code == 201
    body = response.json()
    assert body["title"] == "Write report"
    assert body["priority"] == "high"
    assert body["status"] == "pending"
    assert body["id"] is not None


def test_create_task_with_empty_title_returns_422(client):
    response = client.post("/tasks", json={"title": ""})
    assert response.status_code == 422


def test_create_task_with_invalid_priority_returns_400(client):
    response = client.post("/tasks", json={"title": "Test", "priority": "urgent"})
    assert response.status_code == 400
    assert "priority" in response.json()["detail"].lower()


def test_list_tasks_empty(client):
    response = client.get("/tasks")
    assert response.status_code == 200
    assert response.json() == []


def test_list_tasks_after_creating_some(client):
    client.post("/tasks", json={"title": "Task A"})
    client.post("/tasks", json={"title": "Task B"})

    response = client.get("/tasks")
    assert response.status_code == 200
    assert len(response.json()) == 2


def test_list_tasks_filtered_by_status(client):
    created = client.post("/tasks", json={"title": "Done task"}).json()
    client.post("/tasks", json={"title": "Pending task"})
    client.patch(f"/tasks/{created['id']}/done")

    response = client.get("/tasks", params={"status": "done"})
    assert response.status_code == 200
    results = response.json()
    assert len(results) == 1
    assert results[0]["title"] == "Done task"


def test_get_single_task(client):
    created = client.post("/tasks", json={"title": "Find me"}).json()

    response = client.get(f"/tasks/{created['id']}")
    assert response.status_code == 200
    assert response.json()["title"] == "Find me"


def test_get_nonexistent_task_returns_404(client):
    response = client.get("/tasks/9999")
    assert response.status_code == 404


def test_update_task(client):
    created = client.post("/tasks", json={"title": "Original", "priority": "low"}).json()

    response = client.put(f"/tasks/{created['id']}", json={"priority": "high"})
    assert response.status_code == 200
    body = response.json()
    assert body["priority"] == "high"
    assert body["title"] == "Original"  # untouched field stays the same


def test_update_nonexistent_task_returns_404(client):
    response = client.put("/tasks/9999", json={"priority": "high"})
    assert response.status_code == 404


def test_mark_task_done(client):
    created = client.post("/tasks", json={"title": "Finish me"}).json()

    response = client.patch(f"/tasks/{created['id']}/done")
    assert response.status_code == 200
    assert response.json()["status"] == "done"


def test_delete_task(client):
    created = client.post("/tasks", json={"title": "Temporary"}).json()

    delete_response = client.delete(f"/tasks/{created['id']}")
    assert delete_response.status_code == 204

    get_response = client.get(f"/tasks/{created['id']}")
    assert get_response.status_code == 404


def test_delete_nonexistent_task_returns_404(client):
    response = client.delete("/tasks/9999")
    assert response.status_code == 404
