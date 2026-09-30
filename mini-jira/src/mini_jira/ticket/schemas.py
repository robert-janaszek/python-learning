from typing import Literal

from pydantic import BaseModel, Field, ValidationInfo, field_validator

class TicketDraft(BaseModel):
    title: str
    sender_email: str = Field(description="Address of a person that sends email (From)")
    priority: Literal["low", "medium", "high"]
    tags: list[str]

    @field_validator("sender_email")
    @classmethod
    def validate_email(cls, email: str, info: ValidationInfo[dict[str, object] | None]) -> str:
        if not email:
            raise ValueError("email cannot be empty")
        email_splitted = email.split("@")
        if len(email_splitted) != 2:
            raise ValueError("email must have exactly 1 `@` sign")
        if email_splitted[1].count('.') == 0:
            raise ValueError("domain expected after @ sign")
        if isinstance(info.context, dict):
            source = info.context.get("source")
            if isinstance(source, str) and email not in source:
                raise ValueError("email must appear in the message")
        return email