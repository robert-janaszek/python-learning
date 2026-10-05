from fastapi import APIRouter, status

from mini_jira.qa.schemas import QaResponse, Question
from mini_jira.qa.service import answer_question


router = APIRouter(prefix="/qa")

@router.post("/", status_code=status.HTTP_200_OK, response_model=QaResponse)
async def qa(body: Question):
    return await answer_question(body.question)