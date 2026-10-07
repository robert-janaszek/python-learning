from collections.abc import Mapping
from typing import cast

from fastapi import status
from openai.types.chat import ChatCompletionMessageParam

from mini_jira.agent.call_llm_agent import call_compaction_agent, call_llm_agent
from mini_jira.agent.tools import Tool, handle_tool_call
from mini_jira.agent_messages.schemas import AgentMessageCreate, AgentMessageResponse
from mini_jira.agent_messages.service import AgentMessagesService
from mini_jira.exception import DomainException

from mini_jira.project.service import ProjectService
from mini_jira.project.tools import make_find_project, make_list_projects
from mini_jira.task.service import TaskService
from mini_jira.task.tools import make_count_by_priority, make_create_task, make_list_tasks

class AgentService:
    def __init__(
        self,
        project_service: ProjectService,
        task_service: TaskService,
        agent_message_service: AgentMessagesService
    ):
        self.project_service = project_service
        self.task_service = task_service
        self.agent_message_service = agent_message_service

    async def run_agentic_loop(
        self,
        session_id: str,
    ) -> str:
        list_projects, list_projects_tool = make_list_projects(self.project_service)
        find_project, find_project_tool = make_find_project(self.project_service)
        create_task, create_task_tool = make_create_task(self.task_service, self.project_service)
        list_tasks, list_tasks_tool = make_list_tasks(self.task_service, self.project_service)
        count_by_priority, count_by_priority_tool = make_count_by_priority(self.task_service, self.project_service)

        tools_by_name: Mapping[str, Tool] = {
            "list_projects": list_projects,
            "create_task": create_task,
            "list_tasks": list_tasks,
            "count_by_priority": count_by_priority,
            "find_project": find_project,
        }
    
        compacted_messages = await self.get_messages(session_id)
        messages: list[ChatCompletionMessageParam] = [
            cast(
                ChatCompletionMessageParam,
                { "content": message.content, "role": message.role },
            )
            for message in compacted_messages
        ]

        message_queued = True
        iterations = 0

        while message_queued:
            iterations += 1
            if iterations > 5:
                    raise DomainException(
                        message="The assistant exceeded the step limit",
                        code="ASSISTANT_STEP_LIMIT_EXCEEDED",
                        status_code=status.HTTP_502_BAD_GATEWAY,
                    )
            message_queued = False
            response_message = await call_llm_agent(
                messages,
                [
                    list_projects_tool,
                    create_task_tool,
                    list_tasks_tool,
                    count_by_priority_tool,
                    find_project_tool
                ]
            )

            if response_message.tool_calls:
                message_queued = True
                tool_messages = await handle_tool_call(response_message, tools_by_name)
                messages.extend(tool_messages)

            if not response_message.tool_calls and response_message.content and response_message.content.strip():
                return response_message.content.strip()

        raise DomainException(
            message="The assistant returned no answer",
            code="ASSISTANT_EMPTY_RESPONSE",
            status_code=status.HTTP_502_BAD_GATEWAY,
        )
    
    async def get_messages(self, session_id: str) -> list[AgentMessageResponse]:
        agent_messages = await self.agent_message_service.get_messages(session_id)

        messages_length = sum([len(message.content) for message in agent_messages])

        if messages_length <= 2000:
            return agent_messages

        last_user_index = max(i for i,
            message in enumerate(agent_messages)
            if message.role == "user")
        head = agent_messages[:last_user_index]
        tail = agent_messages[last_user_index:]

        if not head:
            return agent_messages

        summary = await self.compact(head)

        return [summary, *tail]

    async def compact(
        self,
        messages: list[AgentMessageResponse]
    ) -> AgentMessageResponse:
        compacted = await call_compaction_agent(
            [
                cast(
                    ChatCompletionMessageParam,
                    { "content": message.content, "role": message.role },
                )
                for message in messages
            ]
        )
        summary = compacted.content

        if summary is None or not summary.strip():
            raise DomainException(
                message="The assistant returned no answer",
                code="ASSISTANT_EMPTY_RESPONSE",
                status_code=status.HTTP_502_BAD_GATEWAY,
            )
        
        if not summary.startswith("Summary:"):
            summary = f"Summary: {summary}"
        
        await self.agent_message_service.delete_messages(
            messages[0].session_id,
            [message.id for message in messages],
        )
        
        saved = await self.agent_message_service.save_message(
            AgentMessageCreate(
                session_id=messages[0].session_id,
                role="system",
                content=summary,
                created_at=messages[0].created_at,
            )
        )

        return saved
