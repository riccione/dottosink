import time

import typer
from pathlib import Path
from rich.console import Console
from rich.progress import (
    Progress,
    SpinnerColumn,
    TextColumn,
    BarColumn,
    TaskProgressColumn,
)
from rich.table import Table

from scholar_sink.db import DatabaseManager
from scholar_sink.fetcher import search_arxiv, download_pdf

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

    db = DatabaseManager(DB_PATH)

    with Progress(
        SpinnerColumn(),
        TextColumn("[progress.description]{task.description}"),
        BarColumn(),
        TaskProgressColumn(),
        console=console,
    ) as progress:
        # Search Arxiv
        search_task = progress.add_task("Searching Arxiv...", total=None)
        papers = search_arxiv(query, limit)
        progress.update(search_task, description="Search complete", completed=True)

        # Filter out existing papers
        new_papers = [p for p in papers if not db.paper_exists(p.arxiv_id)]

        if not new_papers:
            console.print("[yellow]No new papers to download.[/yellow]")
            return

        # Download new papers
        download_task = progress.add_task(
            "Downloading papers...", total=len(new_papers)
        )

        for i, paper in enumerate(new_papers, 1):
            progress.update(
                download_task,
                description=f"Downloading: {paper.title[:50]}...",
            )

            try:
                pdf_path = download_pdf(paper, RAW_DIR)
                if pdf_path:
                    db.insert_paper(
                        {
                            "arxiv_id": paper.arxiv_id,
                            "title": paper.title,
                            "authors": str(paper.authors),
                            "published": paper.published,
                            "summary": paper.summary,
                            "pdf_path": str(pdf_path),
                            "md_path": None,
                            "status": "downloaded",
                        }
                    )
                    console.print(f"[green]✓[/green] {paper.title[:60]}")
                else:
                    console.print(f"[yellow]⊘[/yellow] {paper.title[:60]} (skipped)")

            except Exception as e:
                console.print(f"[red]✗[/red] {paper.title[:60]}: {e}")

            progress.advance(download_task)

            if i < len(new_papers):
                cooldown_task = progress.add_task("Cooling down (3s)...", total=3)
                for _ in range(3):
                    time.sleep(1)
                    progress.advance(cooldown_task)
                progress.remove_task(cooldown_task)

    console.print(
        f"[bold green]Done![/bold green] Downloaded {len(new_papers)} papers."
    )


@app.command("list-papers")
def list_papers():
    """
    List all papers in the local library.
    """
    db = DatabaseManager(DB_PATH)
    papers = db.get_all_papers()

    if not papers:
        console.print("[yellow]No papers in library.[/yellow]")
        return

    table = Table(title="Local Library")
    table.add_column("ID", style="cyan", no_wrap=True)
    table.add_column("Title", style="white")
    table.add_column("Status", style="green")

    for paper in papers:
        table.add_row(
            paper["arxiv_id"],
            paper["title"][:60] + ("..." if len(paper["title"]) > 60 else ""),
            paper["status"],
        )

    console.print(table)


if __name__ == "__main__":
    app()
