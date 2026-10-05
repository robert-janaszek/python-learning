from pydantic import BaseModel


class Question(BaseModel):
    question: str


class QaResponse(BaseModel):
    answer: str
    quotes: list[str]
