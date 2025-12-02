# regru-api-cli

Interactive CLI for the REG.RU API.

## Features
- Interactive command palette powered by [InquirerPy](https://github.com/kazhala/InquirerPy).
- Authentication via API token pulled from the `REGRU_TOKEN` environment variable or a persisted config file in `~/.regru_cli/config.json`.
- Database-first commands (`db list`, `db create`, `db modify`) with additional categories ready to extend.
- Request/response logging for diagnostics (`~/.regru_cli/regru_cli.log`).
- Basic rate-limit guidance when `IP_EXCEEDED_ALLOWED_CONNECTION_RATE` or `ACCOUNT_EXCEEDED_ALLOWED_CONNECTION_RATE` is returned.

## Installation

```
pip install -e .
```

## Usage

Interactive mode (default):

```
python -m regru_cli
```

Configure persisted credentials:

```
python -m regru_cli configure --token <your_token> --username <default_username>
```

Database commands (non-interactive):

```
python -m regru_cli db list
python -m regru_cli db create <domain_name> <db_name> <db_login> <db_password>
python -m regru_cli db modify <db_id> --password <new_password>
```

Set `REGRU_TOKEN` to override the stored token for one-off sessions. If the API returns rate-limit errors, the CLI will suggest exponential backoff and will not continue until the rate limit window has cooled down.
