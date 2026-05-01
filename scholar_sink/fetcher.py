import time
from pathlib import Path
from typing import List, Optional
import arxiv
import requests

from scholar_sink.models import Paper


def search_arxiv(query: str, limit: int) -> List[Paper]:
    client = arxiv.Client(num_retries=3, delay_seconds=3)
    search = arxiv.Search(query=query, max_results=limit)
    papers = []

    for attempt in range(3):
        try:
            for result in client.results(search):
                arxiv_id = result.entry_id.split("/")[-1]
                paper = Paper(
                    arxiv_id=arxiv_id,
                    title=result.title,
                    authors=[author.name for author in result.authors],
                    published=result.published.isoformat(),
                    summary=result.summary,
                    pdf_path=None,
                    md_path=None,
                    status="pending",
                )
                papers.append(paper)
            return papers

        except arxiv.HTTPError as e:
            if "429" in str(e) and attempt < 2:
                wait_time = (attempt + 1) * 5
                print(f"Rate limit hit. Waiting {wait_time}s before retry...")
                time.sleep(wait_time)
            else:
                raise Exception(
                    f"Arxiv search failed: {e}. "
                    "Please wait a few minutes before trying again."
                ) from e

    return papers


def download_pdf(paper: Paper, folder: Path) -> Optional[Path]:
    raw_dir = folder / "raw"
    raw_dir.mkdir(parents=True, exist_ok=True)

    pdf_filename = f"{paper.arxiv_id.replace('/', '_')}.pdf"
    pdf_path = raw_dir / pdf_filename

    try:
        if pdf_path.exists():
            return pdf_path

        pdf_url = get_pdf_url(paper.arxiv_id)

        response = requests.get(pdf_url, timeout=30)
        response.raise_for_status()

        with open(pdf_path, "wb") as f:
            f.write(response.content)

        return pdf_path

    except requests.HTTPError as e:
        if e.response.status_code in (403, 429):
            raise Exception(
                f"Rate limit hit (HTTP {e.response.status_code}). "
                "Please wait before trying again."
            ) from e
        raise

    finally:
        time.sleep(3)


def get_pdf_url(arxiv_id: str) -> str:
    return f"https://arxiv.org/pdf/{arxiv_id}.pdf"
