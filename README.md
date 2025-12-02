# regru-api-cli

A command-line interface for interacting with the REG.RU API, including database management helpers.

## Prerequisites
- Python 3.10+
- `pip` for dependency installation
- Access to a REG.RU API token with database management permissions

## Setup
1. Clone the repository:
   ```bash
   git clone https://github.com/your-org/regru-api-cli.git
   cd regru-api-cli
   ```
2. Create and activate a virtual environment (recommended):
   ```bash
   python -m venv .venv
   source .venv/bin/activate
   ```
3. Install dependencies:
   ```bash
   pip install -r requirements.txt
   ```

## Configuration
1. Export your REG.RU API token so the CLI can authenticate requests:
   ```bash
   export REGRU_API_TOKEN="<your_api_token>"
   ```
2. Optionally set a default region and logging directory:
   ```bash
   export REGRU_DEFAULT_REGION="ru-central"
   export REGRU_LOG_DIR="$PWD/.logs"
   ```

## Usage
### Basic command pattern
Most commands follow the structure:
```bash
regru-cli <resource> <action> [options]
```

### Interactive database management examples
Start an interactive session for database tasks:
```bash
regru-cli db shell
```
Within the session you can:
- List databases: `db list`
- Create a database: `db create --name example_db --engine postgres`
- Rotate credentials: `db rotate-credentials --name example_db`
- Delete a database: `db delete --name example_db --force`

To run a single command non-interactively:
```bash
regru-cli db create --name example_db --engine postgres
```

### Error handling and retries
- **Rate limits:** When the API returns HTTP 429, the CLI backs off exponentially (starting at 1s, max 30s) and surfaces progress messages. Retries stop after 5 attempts.
- **Network errors:** Transient errors trigger up to 3 retries with jitter; persistent failures print the response body for easier debugging.
- **Authentication issues:** Missing or invalid tokens cause an immediate exit with guidance to re-export `REGRU_API_TOKEN`.

### Logging
- Command logs default to `$REGRU_LOG_DIR` or `~/.regru/logs` if the variable is unset.
- Each run creates a timestamped file containing request IDs, URLs, status codes, and retry notes.
- Enable verbose output with `--verbose` to mirror log lines to stdout.

### Asynchronous usage
REG.RU recommends batching long-running operations asynchronously. The CLI supports async workflows with:
- `--async` flag to enqueue operations and return a task ID immediately.
- `regru-cli tasks list` to view pending and running tasks.
- `regru-cli tasks wait --id <task_id>` to block until completion with periodic status updates.

## Contribution guidelines
1. Fork the repository and create feature branches from `main`.
2. Follow Python style tools configured in the project (e.g., `ruff`, `black` if present).
3. Add tests for new behaviors and run the test suite before opening a PR.
4. Submit descriptive pull requests, including screenshots when changing user-facing output.

## Troubleshooting
- **HTTP 401/403:** Verify `REGRU_API_TOKEN` and that it has required scopes.
- **HTTP 429:** Wait a few minutes or reduce request frequency; the CLI retries automatically with backoff.
- **Timeouts or connection errors:** Check network connectivity or VPN settings and retry with `--verbose` for diagnostics.
- **Unexpected schema errors:** Ensure you are using the latest CLI version (`git pull` and reinstall dependencies).

## License
[MIT](LICENSE)
