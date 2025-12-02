"""Команды для отображения серверов и оборудования."""

from __future__ import annotations

import json

import typer

from ..client import APIError, AuthenticationError, RateLimitError, RegruClient

servers_app = typer.Typer(help="Серверы и оборудование в аккаунте.")


def _render_response(response) -> None:
    typer.echo(json.dumps(response.data, ensure_ascii=False, indent=2))


@servers_app.command("list")
def list_servers(ctx: typer.Context) -> None:
    """Показать все сервера."""

    client = RegruClient(ctx.obj)
    try:
        response = client.list_servers()
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

