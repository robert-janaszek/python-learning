from fastapi import Depends
from sqlalchemy.ext.asyncio import AsyncSession

from mini_jira.agent_messages.repository import AgentMessagesRepository
from mini_jira.agent_messages.service import AgentMessagesService
from mini_jira.database import get_db

def get_agent_messages_repository(
    session: AsyncSession = Depends(get_db)
) -> AgentMessagesRepository:
    return AgentMessagesRepository(session)

def get_agent_messages_service(
    repo: AgentMessagesRepository = Depends(get_agent_messages_repository),
    session: AsyncSession = Depends(get_db)
) -> AgentMessagesService:
    return AgentMessagesService(repo, session)
