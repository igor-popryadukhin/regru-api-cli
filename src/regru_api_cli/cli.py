"""Командный интерфейс для работы с REG.RU API."""

from __future__ import annotations

import json
from typing import Optional

import typer

from .client import APIError, AuthenticationError, RateLimitError, RegruClient
from .commands.config import config_app
from .commands.servers import servers_app
from .commands.services import services_app
from .config import ConfigManager

app = typer.Typer(help="CLI для работы с услугами и серверами REG.RU.")
app.add_typer(config_app, name="config")
app.add_typer(services_app, name="services")
app.add_typer(servers_app, name="servers")


def _load_settings(
    *, base_url: Optional[str] = None, token: Optional[str] = None, username: Optional[str] = None
):
    manager = ConfigManager()
    settings = manager.settings.with_env_overrides()

    if base_url:
        settings.base_url = base_url
    if token:
        settings.token = token
    if username:
        settings.username = username

    return settings


@app.callback()
def main(
    ctx: typer.Context,
    base_url: Optional[str] = typer.Option(
        None, "--base-url", help="Переопределить адрес API для текущего запуска"
    ),
    token: Optional[str] = typer.Option(None, "--token", help="Токен авторизации"),
    username: Optional[str] = typer.Option(None, "--username", help="Имя пользователя по умолчанию"),
) -> None:
    """Инициализирует общий контекст настроек."""

    ctx.obj = _load_settings(base_url=base_url, token=token, username=username)


@app.command()
def ping(ctx: typer.Context) -> None:
    """Проверка соединения и авторизации."""

    client = RegruClient(ctx.obj)
    try:
        response = client.ping()
    except AuthenticationError as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=1) from exc
    except RateLimitError as exc:
        typer.echo(f"Ошибка лимита ({exc.code}): {exc}")
        raise typer.Exit(code=1) from exc
    except APIError as exc:
        typer.echo(f"Ошибка API: {exc}")
        raise typer.Exit(code=1) from exc

    typer.echo("Соединение с API доступно.")
    typer.echo(json.dumps(response.data, ensure_ascii=False, indent=2))


def main_cli() -> None:
    app()


if __name__ == "__main__":
    main_cli()
