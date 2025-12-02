"""Управление конфигурацией CLI."""

from __future__ import annotations

import json
import os
from dataclasses import dataclass, field
from pathlib import Path
from typing import Any, Dict, Optional

DEFAULT_BASE_URL = "https://api.reg.ru/api/regru2"


def _config_dir() -> Path:
    root = os.environ.get("XDG_CONFIG_HOME")
    if root:
        return Path(root) / "regru-api-cli"
    return Path.home() / ".config" / "regru-api-cli"


CONFIG_FILE = _config_dir() / "config.json"


@dataclass
class Settings:
    """Конфигурация для HTTP-клиента."""

    token: Optional[str] = None
    username: Optional[str] = None
    base_url: str = DEFAULT_BASE_URL
    extras: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, raw: Dict[str, Any]) -> "Settings":
        return cls(
            token=raw.get("token"),
            username=raw.get("username"),
            base_url=raw.get("base_url", DEFAULT_BASE_URL),
            extras=raw.get("extras", {}),
        )

    def to_dict(self) -> Dict[str, Any]:
        return {
            "token": self.token,
            "username": self.username,
            "base_url": self.base_url,
            "extras": self.extras,
        }

    def with_env_overrides(self, env: Optional[Dict[str, str]] = None) -> "Settings":
        env_map = env if env is not None else os.environ
        token = env_map.get("REGRU_API_TOKEN", self.token)
        username = env_map.get("REGRU_API_USERNAME", self.username)
        base_url = env_map.get("REGRU_API_URL", self.base_url)
        return Settings(token=token, username=username, base_url=base_url, extras=self.extras)


class ConfigManager:
    """Загрузка и сохранение настроек CLI."""

    def __init__(self, file_path: Path = CONFIG_FILE) -> None:
        self.file_path = file_path
        self._settings = Settings()
        self._load()

    @property
    def settings(self) -> Settings:
        return self._settings

    def _load(self) -> None:
        if not self.file_path.exists():
            return
        try:
            payload = json.loads(self.file_path.read_text())
        except json.JSONDecodeError:
            return
        self._settings = Settings.from_dict(payload)

    def save(self) -> None:
        self.file_path.parent.mkdir(parents=True, exist_ok=True)
        self.file_path.write_text(json.dumps(self._settings.to_dict(), indent=2))

    def update(self, *, token: Optional[str] = None, username: Optional[str] = None, base_url: Optional[str] = None) -> Settings:
        if token is not None:
            self._settings.token = token.strip()
        if username is not None:
            self._settings.username = username.strip() or None
        if base_url is not None:
            self._settings.base_url = base_url.strip() or DEFAULT_BASE_URL
        self.save()
        return self._settings

