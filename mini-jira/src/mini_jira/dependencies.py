from fastapi import Depends
from mini_jira.agent_messages.repository import AgentMessagesRepository
from mini_jira.agent_messages.service import AgentMessagesService
from mini_jira.chat.service import ChatService
from mini_jira.project.repository import ProjectRepository
from mini_jira.project.service import ProjectService
from mini_jira.task.repository import TaskRepository
from mini_jira.task.service import TaskService
from sqlalchemy.ext.asyncio import AsyncSession

from mini_jira.database import get_db

def get_project_repository(
    session: AsyncSession = Depends(get_db)
) -> ProjectRepository:
    return ProjectRepository(session)

def get_project_service(
    repo: ProjectRepository = Depends(get_project_repository),
    session: AsyncSession = Depends(get_db)
) -> ProjectService:
    return ProjectService(repo, session)

def get_task_repository(
    session: AsyncSession = Depends(get_db)
) -> TaskRepository:
    return TaskRepository(session)

def get_task_service(
    task_repository: TaskRepository = Depends(get_task_repository),
    project_repository: ProjectRepository = Depends(get_project_repository),
    session: AsyncSession = Depends(get_db)
) -> TaskService:
    return TaskService(task_repository, project_repository, session)

def get_chat_service():
    return ChatService()

def get_agent_messages_repository(
    session: AsyncSession = Depends(get_db)
) -> AgentMessagesRepository:
    return AgentMessagesRepository(session)

def get_agent_messages_service(
    repo: AgentMessagesRepository = Depends(get_agent_messages_repository),
    session: AsyncSession = Depends(get_db)
) -> AgentMessagesService:
    return AgentMessagesService(repo, session)
