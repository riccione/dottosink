# DottoSink

A local-first scientific research tool for discovering, downloading, and managing Arxiv papers with a clean CLI interface.

## Features

- **Arxiv Integration** - Search and fetch papers directly from Arxiv
- **Local Database** - SQLite-based storage for your paper library
- **Smart Downloads** - Rate-limited PDF downloads with automatic deduplication
- **PDF to Markdown** - Convert downloaded PDFs to clean Markdown using marker with PyMuPDF fallback
- **Text Refinement** - Clean citations and headers from Markdown for AI-ready content
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

# Convert and clean the markdown output
uv run python main.py process --clean
```

The `process` command will:
- Find all papers with status `downloaded`
- Convert PDFs to Markdown using `marker-pdf` (with `PyMuPDF` fallback)
- Optionally clean citations and headers with `--clean` flag
- Save output to `data/vault/`
- Update `md_path` and set status to `processed` in the database
- Mark failed conversions with status `failed`

### View Paper Info

```bash
# View paper details by ID
uv run python main.py info "2401.12345"

# View paper details by partial title match
uv run python main.py info "large language models"
```

The `info` command will:
- Search for a paper by exact Arxiv ID or partial title (case-insensitive)
- Display a formatted card with Title, Authors, Published Date, and Summary
- Print an error message if no paper is found

### Export Processed Papers

```bash
# Export all processed papers (default: data/context_export.md)
uv run python main.py export

# Specify custom output path
uv run python main.py export --output "my_research.md"

# Clean markdown during export
uv run python main.py export --clean
```

The `export` command will:
- Retrieve all papers with status `processed`
- Read each paper's Markdown file from `data/vault/`
- Optionally clean citations and headers with `--clean` flag
- Combine them into a single file with clear separators: `--- # PAPER: [TITLE] ---`
- Show progress with rich progress bars
- Report how many papers were successfully exported

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
│   ├── processor.py           # PDF to Markdown conversion
│   └── refiner.py            # Markdown text cleaning
├── tests/
│   ├── test_ingestion.py      # Ingestion tests
│   ├── test_processor.py      # Processor tests
│   ├── test_cli_tools.py      # CLI tools (info, export) tests
│   └── test_refiner.py        # Refiner (citations, sections) tests
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
