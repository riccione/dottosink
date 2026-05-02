from pathlib import Path
from typing import List, Optional

from sqlite_utils import Database
from sqlite_utils.db import NotFoundError


class DatabaseManager:
    def __init__(self, db_path: Path):
        self.db_path = db_path
        self.db = Database(db_path)
        self.init_db()

    def init_db(self):
        if "papers" not in self.db.table_names():
            self.db["papers"].create(
                {
                    "arxiv_id": str,
                    "title": str,
                    "authors": str,
                    "published": str,
                    "summary": str,
                    "pdf_path": str,
                    "md_path": str,
                    "status": str,
                },
                pk="arxiv_id",
            )

    def insert_paper(self, paper: dict):
        self.db["papers"].insert(paper, replace=True)

    def get_all_papers(self) -> list:
        return list(self.db["papers"].rows)

    def paper_exists(self, arxiv_id: str) -> bool:
        try:
            self.db["papers"].get(arxiv_id)
            return True
        except NotFoundError:
            return False

    def get_papers_by_status(self, status: str) -> list:
        return list(self.db["papers"].rows_where("status = ?", [status]))

    def update_paper(self, arxiv_id: str, updates: dict):
        self.db["papers"].update(arxiv_id, updates)

    def get_paper_by_id(self, arxiv_id: str) -> Optional[dict]:
        try:
            return dict(self.db["papers"].get(arxiv_id))
        except NotFoundError:
            return None

    def get_paper(self, identifier: str) -> Optional[dict]:
        paper = self.get_paper_by_id(identifier)
        if paper:
            return paper

        rows = list(
            self.db["papers"].rows_where(
                "LOWER(title) LIKE ?", [f"%{identifier.lower()}%"]
            )
        )
        if rows:
            return rows[0]

        return None

    def get_processed_papers(self) -> List[dict]:
        return list(self.db["papers"].rows_where("status = ?", ["processed"]))
