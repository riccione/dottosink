from pathlib import Path
from sqlite_utils import Database
from sqlite_utils.db import NotFoundError


class DatabaseManager:
    def __init__(self, db_path: Path):
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
