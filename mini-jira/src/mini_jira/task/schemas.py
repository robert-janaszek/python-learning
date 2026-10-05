from typing import Literal
from pydantic import BaseModel


class TaskCreate(BaseModel):
    title: str
    priority: Literal["low", "medium", "high"]


class TaskResponse(BaseModel):
    id: int
    title: str
    is_completed: bool
    priority: Literal["low", "medium", "high"]
    project_id: int
