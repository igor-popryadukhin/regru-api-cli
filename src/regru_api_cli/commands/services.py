"""Команды для работы с услугами аккаунта."""

from __future__ import annotations

import json

import typer

from ..client import APIError, AuthenticationError, RateLimitError, RegruClient
from ..config import Settings

services_app = typer.Typer(help="Работа с услугами, привязанными к аккаунту.")


def _render_response(response) -> None:
    typer.echo(json.dumps(response.data, ensure_ascii=False, indent=2))


@services_app.command("list")
def list_services(ctx: typer.Context) -> None:
    """Показать все услуги."""

    client = RegruClient(ctx.obj)
    try:
        response = client.list_services()
    except AuthenticationError as exc:
        typer.echo(str(exc))
        raise typer.Exit(code=1) from exc
    except RateLimitError as exc:
        typer.echo(f"Ошибка лимита ({exc.code}): {exc}")
        raise typer.Exit(code=1) from exc
    except APIError as exc:
        typer.echo(f"Ошибка API: {exc}")
        raise typer.Exit(code=1) from exc

    _render_response(response)

