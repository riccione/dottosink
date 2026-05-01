import typer
from pathlib import Path
from rich.console import Console
from scholar_sink.db import DatabaseManager

# Initialize Rich console for pretty output
console = Console()
app = typer.Typer(help="Dottosink: Your local scientific knowledge sink.")

# Configuration
DB_PATH = Path("data/library.db")
RAW_DIR = Path("data/raw")


@app.callback()
def setup():
    """Ensure necessary directories and database exist."""
    RAW_DIR.mkdir(parents=True, exist_ok=True)
    Path("data/vault").mkdir(parents=True, exist_ok=True)
    # Initialize the DB
    DatabaseManager(DB_PATH)


@app.command()
def fetch(query: str, limit: int = 5):
    """
    Search Arxiv and download new papers.
    """
    console.print(f"[bold blue]Searching for:[/bold blue] {query} (Limit: {limit})")
    # Agent will implement the actual logic call here
    console.print("[yellow]Fetcher logic not yet implemented.[/yellow]")


@app.command()
def list_papers():
    """
    List all papers in the local library.
    """
    console.print("[bold green]Local Library:[/bold green]")
    # Agent will implement the table display here
    console.print("[yellow]Database query logic not yet implemented.[/yellow]")


if __name__ == "__main__":
    app()
