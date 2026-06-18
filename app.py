"""FastAPI application exposing TaskManager over HTTP.

This file only handles HTTP concerns: routing, status codes, request/
response shapes. All actual logic still lives in TaskManager — the API
layer is a thin wrapper, the same way main.py was for the CLI. This
means the CLI (main.py) and the API (this file) can both sit on top of
the exact same business logic without duplicating anything.
"""

from __future__ import annotations

from typing import Optional

from fastapi import FastAPI, HTTPException, Query
from fastapi.middleware.cors import CORSMiddleware

from exceptions import InvalidTaskDataError, TaskNotFoundError
from schemas import TaskCreate, TaskResponse, TaskUpdate
from task_manager import TaskManager

app = FastAPI(
    title="Task Manager API",
    description="A simple REST API for managing tasks, built with FastAPI and SQLite.",
    version="1.0.0",
)

# Allows a frontend running on a different origin (e.g. a React app on
# localhost:3000) to call this API during local development/demos.
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

manager = TaskManager()


@app.get("/", tags=["health"])
def read_root() -> dict:
    return {"message": "Task Manager API is running. See /docs for usage."}


@app.post("/tasks", response_model=TaskResponse, status_code=201, tags=["tasks"])
def create_task(payload: TaskCreate) -> TaskResponse:
    try:
        task = manager.create_task(
            title=payload.title,
            description=payload.description,
            priority=payload.priority,
            due_date=payload.due_date,
        )
    except InvalidTaskDataError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return TaskResponse(**task.to_dict())


@app.get("/tasks", response_model=list[TaskResponse], tags=["tasks"])
def list_tasks(
    status: Optional[str] = Query(default=None, description="Filter by 'pending' or 'done'")
) -> list[TaskResponse]:
    tasks = manager.list_tasks(status=status)
    return [TaskResponse(**t.to_dict()) for t in tasks]


@app.get("/tasks/{task_id}", response_model=TaskResponse, tags=["tasks"])
def get_task(task_id: int) -> TaskResponse:
    try:
        task = manager.get_task(task_id)
    except TaskNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return TaskResponse(**task.to_dict())


@app.put("/tasks/{task_id}", response_model=TaskResponse, tags=["tasks"])
def update_task(task_id: int, payload: TaskUpdate) -> TaskResponse:
    fields = {k: v for k, v in payload.model_dump().items() if v is not None}
    try:
        task = manager.update_task(task_id, **fields)
    except TaskNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    except InvalidTaskDataError as exc:
        raise HTTPException(status_code=400, detail=str(exc)) from exc
    return TaskResponse(**task.to_dict())


@app.patch("/tasks/{task_id}/done", response_model=TaskResponse, tags=["tasks"])
def mark_task_done(task_id: int) -> TaskResponse:
    try:
        task = manager.mark_done(task_id)
    except TaskNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
    return TaskResponse(**task.to_dict())


@app.delete("/tasks/{task_id}", status_code=204, tags=["tasks"])
def delete_task(task_id: int) -> None:
    try:
        manager.delete_task(task_id)
    except TaskNotFoundError as exc:
        raise HTTPException(status_code=404, detail=str(exc)) from exc
