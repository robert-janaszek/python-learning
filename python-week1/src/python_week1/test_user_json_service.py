import json
from pathlib import Path
from uuid import UUID

import pytest
from pydantic import ValidationError

from python_week1.user_json_service import UserJsonService
from python_week1.user_payload import UserPayload


@pytest.fixture
def user_json_service() -> UserJsonService:
    return UserJsonService()


USERS_JSON = """
[
{
    "id": "3f1c2a84-7b6e-4d91-9c20-1a8e5f0b6d34",
    "email": "ada@company.com",
    "roles": ["admin", "user"],
    "created_at": "2026-01-12T09:15:00+00:00"
},
{
    "id": "8a44e1c2-0f3b-4e77-b612-9d5c7a1e2f08",
    "email": "linus@company.com",
    "roles": ["admin"],
    "created_at": "2026-02-03T14:40:00+00:00"
}
]
"""

INCORRECT_USERS_JSON = """
[
{
    "id": "3f1c2a84-7b6e-4d91-9c20-1a8e5f0b6d34",
    "email": "ada@company.com",
    "roles": ["user"],
    "created_at": "2026-01-12T09:15:00+00:00"
}
]
"""


def test_load_users(user_json_service: UserJsonService, tmp_path: Path) -> None:
    path = tmp_path / "users.json"
    path.write_text(USERS_JSON, encoding="utf-8")
    users = user_json_service.load_users(path)

    assert len(users) == 2
    assert users[0].id == UUID("3f1c2a84-7b6e-4d91-9c20-1a8e5f0b6d34")
    assert users[1].id == UUID("8a44e1c2-0f3b-4e77-b612-9d5c7a1e2f08")


def test_load_incorrect_users(
    user_json_service: UserJsonService, tmp_path: Path
) -> None:
    path = tmp_path / "users.json"
    path.write_text(INCORRECT_USERS_JSON, encoding="utf-8")
    with pytest.raises(ValidationError):
        user_json_service.load_users(path)


@pytest.mark.asyncio
async def test_process_users(user_json_service: UserJsonService) -> None:
    users = [
        UserPayload(email="ada@company.com", roles=["admin", "user"]),
        UserPayload(email="linus@company.com", roles=["admin"]),
    ]
    users_dict = await user_json_service.process_users(users)

    assert len(users_dict) == 2
    assert users_dict["admin"] == 2
    assert users_dict["user"] == 1


def test_save_stats(user_json_service: UserJsonService, tmp_path: Path) -> None:
    stats = {"admin": 1, "guest": 1}
    stats_file = tmp_path / "stats.json"
    user_json_service.save_stats(stats_file, stats)
    raw = stats_file.read_text(encoding="utf-8")
    assert json.loads(raw) == stats
