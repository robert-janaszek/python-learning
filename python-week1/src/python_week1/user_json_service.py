import asyncio
import json
from collections import defaultdict
from pathlib import Path

from python_week1.user_payload import UserPayload


class UserJsonService:
    def load_users(self, path: Path) -> list[UserPayload]:
        raw = path.read_text(encoding="utf-8")
        users = json.loads(raw)
        users_parsed = [UserPayload.model_validate(user) for user in users]

        return users_parsed

    async def process_users(self, users: list[UserPayload]) -> dict[str, int]:
        roles_dict = defaultdict[str, int](int)

        workers = asyncio.Semaphore(3)

        async def process_one(user: UserPayload) -> None:
            async with workers:
                return await self.process_user(user, roles_dict)

        await asyncio.gather(*(process_one(user) for user in users))

        return dict[str, int](roles_dict)

    async def process_user(
        self, user: UserPayload, roles_dict: defaultdict[str, int]
    ) -> None:
        await asyncio.sleep(1)
        print(f"processed {user.id}")
        for role in user.roles:
            roles_dict[role] += 1

    def save_stats(self, path: Path, stats: dict[str, int]) -> None:
        raw = json.dumps(stats)
        path.write_text(raw, encoding="utf-8")
