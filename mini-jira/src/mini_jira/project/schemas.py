from datetime import datetime, UTC
from pydantic import BaseModel, Field


class ProjectCreate(BaseModel):
    name: str
    description: str | None


class ProjectResponse(BaseModel):
    id: int
    name: str
    created_at: datetime = Field(default_factory=lambda: datetime.now(UTC))


class ProjectsResponse(ProjectResponse):
    task_count: int
