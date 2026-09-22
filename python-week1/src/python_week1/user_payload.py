from datetime import datetime, timezone
from typing import Literal, Self
from uuid import UUID, uuid4
from pydantic import BaseModel, EmailStr, Field, field_validator, model_validator


class UserPayload(BaseModel):
    id: UUID = Field(default_factory=uuid4)
    email: EmailStr
    roles: list[Literal["admin", "user", "guest"]]
    created_at: datetime = Field(default_factory=lambda: datetime.now(timezone.utc))
    
    @field_validator("roles")
    @classmethod
    def validate_role(cls, value):
        if not value:
            raise ValueError("roles cannot be empty")
        return value

    @model_validator(mode="after")
    def role_is_admin(self) -> Self:
        if not self.email.endswith("@company.com"):
            return self
        if "admin" in self.roles:
            return self
        raise ValueError("User with company.com email has to be admin")
