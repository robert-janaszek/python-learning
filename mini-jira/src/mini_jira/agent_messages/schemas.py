from datetime import datetime
from typing import Literal
from pydantic import BaseModel


class AgentMessageCreate(BaseModel):
    session_id: str
    role: Literal["system", "user", "assistant", "tool"]
    content: str


class AgentMessageResponse(BaseModel):
    id: int
    session_id: str
    role: Literal["system", "user", "assistant", "tool"]
    content: str
    created_at: datetime

class AgentSendMessage(BaseModel):
    content: str
