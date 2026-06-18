

from __future__ import annotations

from typing import Optional

from pydantic import BaseModel, Field


class TaskCreate(BaseModel):
    title: str = Field(..., min_length=1, json_schema_extra={"example": "Write quarterly report"})
    description: str = Field(default="", json_schema_extra={"example": "Summarize Q2 sales performance"})
    priority: str = Field(default="medium", json_schema_extra={"example": "high"})
    due_date: Optional[str] = Field(default=None, json_schema_extra={"example": "2026-06-30"})


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
