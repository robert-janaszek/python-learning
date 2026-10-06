from fastapi import Depends
from mini_jira.agent.service import AgentService
from mini_jira.agent_messages.dependencies import get_agent_messages_service
from mini_jira.agent_messages.service import AgentMessagesService
from mini_jira.project.dependencies import get_project_service
from mini_jira.project.service import ProjectService
from mini_jira.task.dependencies import get_task_service
from mini_jira.task.service import TaskService


def get_agent_service(
    project_service: ProjectService = Depends(get_project_service),
    task_service: TaskService = Depends(get_task_service),
    agent_message_service: AgentMessagesService = Depends(get_agent_messages_service),
) -> AgentService:
    return AgentService(project_service, task_service, agent_message_service)
