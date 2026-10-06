from typing import Protocol
from sqlalchemy import insert, select
from sqlalchemy.ext.asyncio import AsyncSession
from collections.abc import Sequence

from mini_jira.agent_messages.schemas import AgentMessageCreate
from mini_jira.models import AgentMessagesModel


class AgentMessagesRepositoryProtocol(Protocol):
    async def get_messages(self, session_id: str) -> Sequence[AgentMessagesModel]: ...
    async def save_message(self, payload: AgentMessageCreate) -> AgentMessagesModel: ...


class AgentMessagesRepository:
    def __init__(self, session: AsyncSession):
        self.session = session

    async def get_messages(self, session_id: str) -> Sequence[AgentMessagesModel]:
        select_stmt = select(
            AgentMessagesModel
        ).where(
            AgentMessagesModel.session_id == session_id
        ).order_by(AgentMessagesModel.created_at, AgentMessagesModel.id)
        result = await self.session.execute(select_stmt)

        return result.scalars().all()
    
    async def save_message(self, payload: AgentMessageCreate) -> AgentMessagesModel:
        insert_stmt = (
            insert(AgentMessagesModel)
            .values(
                session_id=payload.session_id,
                role=payload.role,
                content=payload.content,
            )
            .returning(AgentMessagesModel)
        )

        result = await self.session.execute(insert_stmt)

        return result.scalar_one()

        
