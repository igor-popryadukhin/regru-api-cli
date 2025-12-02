from __future__ import annotations

import json
import logging
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

CONFIG_DIR = Path.home() / ".regru_cli"
CONFIG_FILE = CONFIG_DIR / "config.json"
LOG_FILE = CONFIG_DIR / "regru_cli.log"


@dataclass
class CLIConfig:
    """Serializable configuration for the CLI."""

    token: Optional[str] = None
    username: Optional[str] = None
    log_level: str = "INFO"
    extras: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        return {
            "token": self.token,
            "username": self.username,
            "log_level": self.log_level,
            "extras": self.extras,
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "CLIConfig":
        return cls(
            token=data.get("token"),
            username=data.get("username"),
            log_level=data.get("log_level", "INFO"),
            extras=data.get("extras", {}),
        )


class ConfigManager:
    """Handles persistence and retrieval of CLI configuration."""

    def __init__(self) -> None:
        CONFIG_DIR.mkdir(parents=True, exist_ok=True)
        self._config = CLIConfig()
        self._load()
        self._configure_logging()

    @property
    def config(self) -> CLIConfig:
        return self._config

    def _load(self) -> None:
        if CONFIG_FILE.exists():
            try:
                content = json.loads(CONFIG_FILE.read_text())
                self._config = CLIConfig.from_dict(content)
            except json.JSONDecodeError:
                logging.getLogger(__name__).warning(
                    "Config file %s is not valid JSON; using defaults.", CONFIG_FILE
                )

    def save(self) -> None:
        CONFIG_FILE.write_text(json.dumps(self._config.to_dict(), indent=2))

    def set_token(self, token: str) -> None:
        self._config.token = token.strip()
        self.save()

    def set_username(self, username: str) -> None:
        self._config.username = username.strip()
        self.save()

    def _configure_logging(self) -> None:
        handlers: list[logging.Handler] = []
        file_handler = logging.FileHandler(LOG_FILE)
        formatter = logging.Formatter(
            "%(asctime)s [%(levelname)s] %(name)s - %(message)s"
        )
        file_handler.setFormatter(formatter)
        handlers.append(file_handler)

        logging.basicConfig(
            level=getattr(logging, self._config.log_level.upper(), logging.INFO),
            handlers=handlers,
        )


def get_token_from_env(env: Optional[Dict[str, str]] = None) -> Optional[str]:
    """Return token from environment if available."""

    env_map = env if env is not None else os.environ
    return env_map.get("REGRU_TOKEN")
