# DottoSink

A local-first scientific research tool for discovering, downloading, and managing Arxiv papers with a clean CLI interface.

## Features

- **Arxiv Integration** - Search and fetch papers directly from Arxiv
- **Local Database** - SQLite-based storage for your paper library
- **Smart Downloads** - Rate-limited PDF downloads with automatic deduplication
- **Rich CLI** - Beautiful terminal output with progress bars and tables
- **Extensible** - Built with modular architecture for easy feature additions

## Installation

### Prerequisites

- Python 3.13+
- [uv](https://docs.astral.sh/uv/) package manager

### Quick Start

```bash
# Clone the repository
git clone https://github.com/yourusername/dottosink.git
cd dottosink

# Install dependencies
uv sync

# Install the package in editable mode
uv pip install -e .
```

## Usage

### Search and Download Papers

```bash
# Search for papers (defaults to 5 results)
uv run python main.py fetch "large language models"

# Specify number of results
uv run python main.py fetch "transformer architecture" --limit 10
```

The `fetch` command will:
- Search Arxiv for your query
- Skip papers already in your library
- Download PDFs to `data/raw/` with a 3-second rate limit delay
- Show progress with rich progress bars

### List Your Library

```bash
uv run python main.py list-papers
```

Displays all papers in your local library with ID, title, and status.

## Development

### Setup Development Environment

```bash
# Install development dependencies
uv sync --extra dev
```

### Running Tests

```bash
# Run all tests
uv run pytest

# Run tests with verbose output
uv run pytest -v

# Run specific test file
uv run pytest tests/test_ingestion.py -v
```

### Code Quality

```bash
# Lint and format code
uv run ruff check --fix .
uv run ruff format .
```

## Project Structure

```
dottosink/
├── main.py                    # CLI entry point
├── scholar_sink/
│   ├── __init__.py
│   ├── db.py                  # Database management
│   ├── fetcher.py             # Arxiv API and PDF downloads
│   └── models.py              # Pydantic data models
├── tests/
│   └── test_ingestion.py      # Test suite
├── data/
│   ├── library.db             # SQLite database
│   ├── raw/                   # Downloaded PDFs
│   └── vault/                 # Processed content
└── pyproject.toml             # Project configuration
```

## Dependencies

- **arxiv** - Arxiv API client
- **typer** - CLI framework
- **rich** - Terminal formatting
- **pydantic** - Data validation
- **sqlite-utils** - Database operations
- **marker-pdf** - PDF processing (future use)

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feat/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feat/amazing-feature`)
5. Open a Pull Request
