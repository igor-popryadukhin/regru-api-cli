"""Command line interface for the REG.RU API client."""

import httpx
import typer

from . import __version__

app = typer.Typer(help="CLI for interacting with the REG.RU API.")


@app.command()
def ping(base_url: str = "https://api.example.com") -> None:
    """Prepare an HTTP client for the provided API base URL."""

    with httpx.Client(base_url=base_url, headers={"User-Agent": f"regru-cli/{__version__}"}) as client:
        typer.echo(f"Prepared HTTP client for {client.base_url}")


def main() -> None:
    """Entrypoint for console script."""

    app()


if __name__ == "__main__":
    main()
