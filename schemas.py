"""Pydantic schemas for the API layer.

These are deliberately separate from the Task dataclass in task.py.
Task is the internal domain model; these schemas define the public
HTTP contract (what clients send and receive). Keeping them apart
means the API shape can evolve independently of internal storage.
"""

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, example="Write quarterly report")
    description: str = Field(default="", example="Summarize Q2 sales performance")
    priority: str = Field(default="medium", example="high")
    due_date: Optional[str] = Field(default=None, example="2026-06-30")


class TaskUpdate(BaseModel):
    """All fields optional — only provided fields are changed (PATCH-style update)."""

    title: Optional[str] = None
    description: Optional[str] = None
    priority: Optional[str] = None
    status: Optional[str] = None
    due_date: Optional[str] = None


class TaskResponse(BaseModel):
    id: int
    title: str
    description: str
    priority: str
    status: str
    due_date: Optional[str]
    created_at: str
