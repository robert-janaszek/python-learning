from fastapi import APIRouter, Depends, status
from fastapi.responses import StreamingResponse

from mini_jira.chat.dependencies import get_chat_service
from mini_jira.chat.schemas import ChatPrompt
from mini_jira.chat.service import ChatService


router = APIRouter(prefix="/chat")

@router.post("/", status_code=status.HTTP_200_OK)
async def chat(body: ChatPrompt, chat_service: ChatService = Depends(get_chat_service)):
    return StreamingResponse(chat_service.chat(body.prompt), media_type="text/plain")
