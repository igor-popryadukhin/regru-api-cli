from __future__ import annotations

import json
from typing import Any, Dict

from InquirerPy import inquirer

from .client import AuthenticationError, RateLimitError, RegruClient
from .config import ConfigManager


class CLI:
    def __init__(self) -> None:
        self.config_manager = ConfigManager()
        self.client = RegruClient(self.config_manager)

    def run_interactive(self) -> None:
        while True:
            choice = inquirer.select(
                message="Select a command",
                choices=[
                    "db list",
                    "db create",
                    "db modify",
                    "configure",
                    "exit",
                ],
            ).execute()

            if choice == "db list":
                self._handle_db_list()
            elif choice == "db create":
                self._handle_db_create()
            elif choice == "db modify":
                self._handle_db_modify()
            elif choice == "configure":
                self._configure()
            elif choice == "exit":
                return

    def _configure(self) -> None:
        token = inquirer.text(message="Enter API token", default=self.config_manager.config.token or "").execute()
        username = inquirer.text(
            message="Default username (optional)", default=self.config_manager.config.username or ""
        ).execute()
        if token:
            self.config_manager.set_token(token)
        if username:
            self.config_manager.set_username(username)
        print("Configuration saved in", self.config_manager.config)

    def _handle_db_list(self) -> None:
        domain_name = inquirer.text(message="Filter by domain (optional)", default="").execute()
        params: Dict[str, Any] = {}
        if domain_name:
            params["domain_name"] = domain_name
        self._call_and_render(lambda: self.client.list_databases(**params))

    def _handle_db_create(self) -> None:
        domain_name = inquirer.text(message="Domain name", validate=lambda v: len(v) > 0).execute()
        db_name = inquirer.text(message="Database name", validate=lambda v: len(v) > 0).execute()
        db_login = inquirer.text(message="DB user login", validate=lambda v: len(v) > 0).execute()
        db_password = inquirer.secret(message="DB user password", validate=lambda v: len(v) >= 8).execute()
        self._call_and_render(
            lambda: self.client.create_database(
                domain_name=domain_name, db_name=db_name, db_login=db_login, db_password=db_password
            )
        )

    def _handle_db_modify(self) -> None:
        db_id = inquirer.text(message="Database ID", validate=lambda v: len(v) > 0).execute()
        new_password = inquirer.secret(
            message="New password (leave empty to skip)",
            default="",
        ).execute()
        changes: Dict[str, Any] = {}
        if new_password:
            changes["db_password"] = new_password
        if not changes:
            print("Nothing to update.")
            return
        self._call_and_render(lambda: self.client.modify_database(db_id=db_id, **changes))

    def _call_and_render(self, func: Any) -> None:
        try:
            response = func()
        except AuthenticationError as exc:
            print(f"Authentication error: {exc}")
            return
        except RateLimitError as exc:
            print(f"Rate limit hit ({exc.code}). {exc} Consider retrying with exponential backoff.")
            return
        except Exception as exc:  # noqa: BLE001
            print(f"Unexpected error: {exc}")
            return

        if response.is_success:
            print("Success")
        else:
            print(f"Result: {response.result}")
        print(json.dumps(response.data, indent=2))


def run_interactive() -> None:
    CLI().run_interactive()
