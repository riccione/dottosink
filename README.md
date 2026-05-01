# DottoSink

A local-first scientific research tool for discovering, downloading, and managing Arxiv papers with a clean CLI interface.

## Features

- **Arxiv Integration** - Search and fetch papers directly from Arxiv
- **Local Database** - SQLite-based storage for your paper library
- **Smart Downloads** - Rate-limited PDF downloads with automatic deduplication
- **PDF to Markdown** - Convert downloaded PDFs to clean Markdown using marker with PyMuPDF fallback
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

### Convert PDFs to Markdown

```bash
# Convert all downloaded PDFs to Markdown
uv run python main.py process
```

The `process` command will:
- Find all papers with status `downloaded`
- Convert PDFs to Markdown using `marker-pdf` (with `PyMuPDF` fallback)
- Save output to `data/vault/`
- Update `md_path` and set status to `processed` in the database
- Mark failed conversions with status `failed`

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
│   ├── models.py              # Pydantic data models
│   └── processor.py           # PDF to Markdown conversion
├── tests/
│   ├── test_ingestion.py      # Ingestion tests
│   └── test_processor.py      # Processor tests
├── data/
│   ├── library.db             # SQLite database
│   ├── raw/                   # Downloaded PDFs
│   └── vault/                 # Processed Markdown files
└── pyproject.toml             # Project configuration
```

## Dependencies

- **arxiv** - Arxiv API client
- **typer** - CLI framework
- **rich** - Terminal formatting
- **pydantic** - Data validation
- **sqlite-utils** - Database operations
- **marker-pdf** - PDF to Markdown conversion
- **PyMuPDF** - Fallback PDF text extraction

## License

This project is licensed under the Apache License 2.0 - see the LICENSE file for details.

## Contributing

Contributions are welcome! Please feel free to submit a Pull Request.

1. Fork the repository
2. Create your feature branch (`git checkout -b feat/amazing-feature`)
3. Commit your changes (`git commit -m 'feat: add amazing feature'`)
4. Push to the branch (`git push origin feat/amazing-feature`)
5. Open a Pull Request
