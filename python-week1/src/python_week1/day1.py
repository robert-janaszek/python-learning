import asyncio
import time
from collections import defaultdict
from typing import TypedDict

from pydantic import ValidationError

from python_week1.fetch_metrics import fetch_all
from python_week1.rate_limiter import RateLimiter
from python_week1.timer import Timer
from python_week1.user_payload import UserPayload


class Log(TypedDict):
    user_id: int
    action: str
    duration: int


def Day1() -> None:
    logs: list[Log] = [
        {"user_id": 1, "action": "login", "duration": 120},
        {"user_id": 2, "action": "login", "duration": 110},
        {"user_id": 1, "action": "logout", "duration": 90},
        {"user_id": 1, "action": "login", "duration": 30},
    ]
    logins = login_durations(logs)
    print(logins)
    durations = last_login_duration(logs)
    print(durations)
    totals = total_login_duration(logs)
    print(totals)

    limiter = RateLimiter(3, 1)
    print(limiter)

    allowed = limiter("123")
    print(allowed)
    limiter("123")
    limiter("123")
    allowed = limiter("123")
    print(allowed)

    with Timer("RateLimiter"):
        time.sleep(0.1)

    try:
        UserPayload.model_validate({"email": "me@me.com", "roles": [""]})
    except ValidationError as err:
        print("user payload creation error occurred")
        print(err)

    try:
        UserPayload(email="me@me.com", roles=[])
    except ValidationError as err:
        print("user payload creation error occurred")
        print(err)

    try:
        UserPayload.model_validate_json('{ "id": 1, "email": "me@company.com" }')
    except ValidationError as err:
        print("json validation failed")
        print(err)

    try:
        UserPayload.model_validate_json(
            '{ "email": "me@company.com", "roles": ["admin"] }'
        )
    except ValidationError as err:
        print("json validation failed")
        print(err)
    else:
        print("Payload is correct")

    asyncio.run(fetch_all())


def login_durations(logs: list[Log]) -> list[int]:
    return [l["duration"] for l in logs if l["action"] == "login"]


def last_login_duration(logs: list[Log]) -> dict[int, int]:
    return {l["user_id"]: l["duration"] for l in logs if l["action"] == "login"}


def total_login_duration(logs: list[Log]) -> dict[int, int]:
    totals = defaultdict[int, int](int)

    for log in logs:
        if log["action"] == "login":
            totals[log["user_id"]] += log["duration"]

    return dict[int, int](totals)
