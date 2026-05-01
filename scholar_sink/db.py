import sqlite3
from pathlib import Path
from sqlite_utils import Database

class DatabaseManager:
    def __init__(self, db_path: Path):
        self.db = Database(db_path)
        self.init_db()

    def init_db(self):
        # Create table if not exists using the Paper model schema
        if "papers" not in self.db.table_names():
            self.db["papers"].create({
                "arxiv_id": str,
                "title": str,
                "authors": str,
                "published": str,
                "summary": str,
                "pdf_path": str,
                "md_path": str,
                "status": str
            }, pk="arxiv_id")
