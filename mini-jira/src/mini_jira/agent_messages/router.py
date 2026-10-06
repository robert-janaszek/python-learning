from fastapi import APIRouter, Depends, status

from mini_jira.agent.dependencies import get_agent_service
from mini_jira.agent.service import AgentService
from mini_jira.agent_messages.dependencies import get_agent_messages_service
from mini_jira.agent_messages.schemas import AgentMessageCreate, AgentSendMessage
from mini_jira.agent_messages.service import AgentMessagesService


router = APIRouter(prefix="/agent")

@router.post("/{session_id}/messages/", status_code=status.HTTP_200_OK)
async def send_agent_message(
    session_id: str,
    payload: AgentSendMessage,
    agent_message_service: AgentMessagesService = Depends(get_agent_messages_service),
    agent_service: AgentService = Depends(get_agent_service),
):
    await agent_message_service.save_message(AgentMessageCreate(
        session_id=session_id,
        content=payload.content,
        role="user",
    ))

    # run_agentic_loop(session_id, )
    answer = await agent_service.run_agentic_loop(session_id)

    # response = agent
    # await agent_message_service.save_message(AgentMessageCreate(
    #     session_id=session_id,
    #     content=response,
    #     role="assistant",
    # ))
    return answer
