# model.py — Pydantic schemas and enums for the Task Manager API

from pydantic import BaseModel, Field
from datetime import date
from enum import Enum
from typing import Optional


class Priority(str, Enum):
    low    = "low"
    medium = "medium"
    high   = "high"


class Status(str, Enum):
    todo        = "todo"
    in_progress = "in_progress"
    done        = "done"


class TaskCreate(BaseModel):
    """Fields the client sends when creating a new task."""
    title:       str            = Field(min_length=1, max_length=120,
                                        description="Short task title")
    description: Optional[str] = Field(None, description="Optional longer description")
    priority:    Priority       = Field(Priority.medium, description="low / medium / high")
    due_date:    Optional[date] = Field(None, description="Due date in YYYY-MM-DD format")


class TaskUpdate(BaseModel):
    """
    Fields the client sends when updating a task.
    Every field is optional — only fields you include will change.
    """
    title:       Optional[str]      = Field(None, min_length=1, max_length=120)
    description: Optional[str]      = None
    priority:    Optional[Priority] = None
    status:      Optional[Status]   = None
    due_date:    Optional[date]     = None