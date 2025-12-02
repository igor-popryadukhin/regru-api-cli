# regru-api-cli

CLI for REG.RU API interactions.

## Installation

Install the package and console entrypoint with pip:

```
pip install .
```

After installation, invoke the CLI via the `regru-cli` command or by running the module:

```
regru-cli --help
python -m regru_api_cli ping --base-url https://api.example.com
```

## Development

Create a virtual environment and install the development dependencies:

```
python -m venv .venv
source .venv/bin/activate
pip install -r requirements-dev.txt
pre-commit install
```

Run the formatters and linters manually with:

```
ruff check src
ruff format src
black src
```
