from __future__ import annotations

import argparse
import json
import sys

from .client import AuthenticationError, RateLimitError, RegruClient
from .cli import run_interactive
from .config import ConfigManager


def _print_response(response) -> None:
    if response.is_success:
        print("Success")
    else:
        print(f"Result: {response.result}")
    print(json.dumps(response.data, indent=2))


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description="Interactive REG.RU API CLI")
    subparsers = parser.add_subparsers(dest="command")

    # Configure
    config_parser = subparsers.add_parser("configure", help="Persist token and defaults")
    config_parser.add_argument("--token", help="API token", required=False)
    config_parser.add_argument("--username", help="Default username", required=False)

    # Database commands
    db_parser = subparsers.add_parser("db", help="Database commands")
    db_sub = db_parser.add_subparsers(dest="db_command")

    db_sub.add_parser("list", help="List databases")

    create_parser = db_sub.add_parser("create", help="Create a database")
    create_parser.add_argument("domain_name")
    create_parser.add_argument("db_name")
    create_parser.add_argument("db_login")
    create_parser.add_argument("db_password")

    modify_parser = db_sub.add_parser("modify", help="Modify a database")
    modify_parser.add_argument("db_id")
    modify_parser.add_argument("--password", dest="db_password", help="New database password")

    return parser


def main(argv: list[str] | None = None) -> int:
    argv = argv or sys.argv[1:]
    parser = build_parser()
    args = parser.parse_args(argv)

    if not args.command:
        run_interactive()
        return 0

    config_manager = ConfigManager()
    client = RegruClient(config_manager)

    if args.command == "configure":
        if args.token:
            config_manager.set_token(args.token)
        if args.username:
            config_manager.set_username(args.username)
        print("Configuration saved to", config_manager.config)
        return 0

    if args.command == "db":
        try:
            if args.db_command == "list":
                response = client.list_databases()
            elif args.db_command == "create":
                response = client.create_database(
                    domain_name=args.domain_name,
                    db_name=args.db_name,
                    db_login=args.db_login,
                    db_password=args.db_password,
                )
            elif args.db_command == "modify":
                if not args.db_password:
                    parser.error("--password is required to modify the database password")
                response = client.modify_database(args.db_id, db_password=args.db_password)
            else:
                parser.error("Unknown db command")
                return 1
        except AuthenticationError as exc:
            print(f"Authentication error: {exc}")
            return 1
        except RateLimitError as exc:
            print(f"Rate limit hit ({exc.code}). {exc} Try again later.")
            return 1
        except Exception as exc:  # noqa: BLE001
            print(f"Unexpected error: {exc}")
            return 1

        _print_response(response)
        return 0

    parser.error("Unknown command")
    return 1


if __name__ == "__main__":
    raise SystemExit(main())
