"""Команды для управления конфигурацией."""

from __future__ import annotations

import typer

from ..config import ConfigManager

config_app = typer.Typer(help="Настройка токена и адреса API.")


@config_app.command("show")
def show() -> None:
    """Показать текущие настройки из файла и переменных окружения."""

    settings = ConfigManager().settings.with_env_overrides()
    typer.echo(f"Базовый URL: {settings.base_url}")
    typer.echo(f"Имя пользователя: {settings.username or 'не задано'}")
    typer.echo("Токен: задан" if settings.token else "Токен: не задан")


@config_app.command("set-token")
def set_token(token: str) -> None:
    """Сохранить токен в файл конфигурации."""

    manager = ConfigManager()
    manager.update(token=token)
    typer.echo("Токен сохранён.")


@config_app.command("set-endpoint")
def set_endpoint(base_url: str) -> None:
    """Сохранить базовый URL API в файл конфигурации."""

    manager = ConfigManager()
    manager.update(base_url=base_url)
    typer.echo(f"Новый адрес API: {manager.settings.base_url}")


@config_app.command("set-username")
def set_username(username: str) -> None:
    """Сохранить имя пользователя по умолчанию."""

    manager = ConfigManager()
    manager.update(username=username)
    typer.echo(f"Имя пользователя сохранено: {manager.settings.username}")

