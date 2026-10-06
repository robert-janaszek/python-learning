from sqlalchemy.ext.asyncio import AsyncSession
from mini_jira.agent_messages.repository import AgentMessagesRepositoryProtocol
from mini_jira.agent_messages.schemas import AgentMessageCreate, AgentMessageResponse

class AgentMessagesService:
    def __init__(self, agent_messages_repository: AgentMessagesRepositoryProtocol, session: AsyncSession):
        self.agent_messages_repository = agent_messages_repository
        self.session = session
    
    async def get_messages(self, session_id: str) -> list[AgentMessageResponse]:
        messages = await self.agent_messages_repository.get_messages(session_id)

        return [
            AgentMessageResponse(
                id=message.id,
                session_id=message.session_id,
                role=message.role,
                content=message.content,
                created_at=message.created_at,
            )
            for message in messages
        ]

    async def save_message(self, payload: AgentMessageCreate) -> AgentMessageResponse:
        message = await self.agent_messages_repository.save_message(payload)
        await self.session.commit()

        return AgentMessageResponse(
            id=message.id,
            session_id=message.session_id,
            role=message.role,
            content=message.content,
            created_at=message.created_at,
        )

