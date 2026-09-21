from collections import defaultdict

def main() -> None:
    logs = [
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
    


def login_durations(logs: list[dict]) -> list[int]:
    return [l["duration"] for l in logs if l["action"] == "login"]

def last_login_duration(logs: list[dict]) -> dict[int, int]:
    return { l["user_id"]: l["duration"] for l in logs if l["action"] == "login"}

def total_login_duration(logs: list[dict]) -> dict[int, int]:
    totals = defaultdict(int)
    
    for log in logs:
        if log["action"] == "login":
            totals[log["user_id"]] += log["duration"]
    
    return dict(totals)