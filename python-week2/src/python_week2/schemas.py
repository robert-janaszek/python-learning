from datetime import datetime, UTC
from typing import Literal
from pydantic import BaseModel, Field

class ProjectCreate(BaseModel):
    name: str
    description: str | None


class ProjectResponse(BaseModel):
    id: int
    name: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class TaskCreate(BaseModel):
    title: str
    priority: Literal["low", "medium", "high"]


class TaskResponse(BaseModel):
    id: int
    title: str
    is_completed: bool
    project_id: int
