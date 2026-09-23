import asyncio
from argparse import ArgumentParser
from pathlib import Path

from python_week1.user_json_service import UserJsonService


def main() -> None:
    parser = ArgumentParser()
    parser.add_argument("path")
    parser.add_argument("output_path")
    args = parser.parse_args()
    path = Path(args.path)
    output_path = Path(args.output_path)

    user_json_service = UserJsonService()
    users = user_json_service.load_users(path)
    roles = asyncio.run(user_json_service.process_users(users))

    user_json_service.save_stats(output_path, roles)


if __name__ == "__main__":
    main()
