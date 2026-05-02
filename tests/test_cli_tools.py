import sys
from pathlib import Path
from unittest.mock import patch, MagicMock

import pytest

from scholar_sink.db import DatabaseManager

sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def temp_db(tmp_path):
    db_path = tmp_path / "test.db"
    return DatabaseManager(db_path)


@pytest.fixture
def populated_db(temp_db):
    papers = [
        {
            "arxiv_id": "2401.12345",
            "title": "Large Language Models Survey",
            "authors": "['Author One']",
            "published": "2024-01-01",
            "summary": "A comprehensive survey on LLMs.",
            "pdf_path": "/tmp/2401.12345.pdf",
            "md_path": "/tmp/vault/2401.12345.md",
            "status": "processed",
        },
        {
            "arxiv_id": "2402.54321",
            "title": "Transformer Architecture Advances",
            "authors": "['Author Two']",
            "published": "2024-02-15",
            "summary": "Recent advances in transformer models.",
            "pdf_path": "/tmp/2402.54321.pdf",
            "md_path": "/tmp/vault/2402.54321.md",
            "status": "processed",
        },
    ]
    for p in papers:
        temp_db.insert_paper(p)

    vault_dir = Path("/tmp/vault")
    vault_dir.mkdir(exist_ok=True)
    for p in papers:
        md_path = Path(p["md_path"])
        md_path.write_text(f"# {p['title']}\n\nPaper content here.", encoding="utf-8")

    return temp_db


class TestInfoCommand:
    def test_info_by_id_prints_panel(self, populated_db, monkeypatch, capsys):
        from main import app
        from typer.testing import CliRunner

        runner = CliRunner()
        monkeypatch.setattr("main.DB_PATH", populated_db.db_path)

        result = runner.invoke(app, ["info", "2401.12345"])

        assert result.exit_code == 0
        assert "Large Language Models Survey" in result.output
        assert "Author One" in result.output
        assert "A comprehensive survey on LLMs." in result.output

    def test_info_by_title_partial_match(self, populated_db, monkeypatch):
        from main import app
        from typer.testing import CliRunner

        runner = CliRunner()
        monkeypatch.setattr("main.DB_PATH", populated_db.db_path)

        result = runner.invoke(app, ["info", "Transformer"])

        assert result.exit_code == 0
        assert "Transformer Architecture Advances" in result.output

    def test_info_not_found_prints_error(self, temp_db, monkeypatch):
        from main import app
        from typer.testing import CliRunner

        runner = CliRunner()
        monkeypatch.setattr("main.DB_PATH", temp_db.db_path)

        result = runner.invoke(app, ["info", "nonexistent"])

        assert result.exit_code == 0
        assert "No paper found" in result.output


class TestExportCommand:
    def test_export_creates_file_with_headers(self, populated_db, tmp_path, monkeypatch):
        from main import app
        from typer.testing import CliRunner

        runner = CliRunner()
        monkeypatch.setattr("main.DB_PATH", populated_db.db_path)
        monkeypatch.setattr("main.VAULT_DIR", Path("/tmp/vault"))

        output_file = tmp_path / "export.md"
        result = runner.invoke(app, ["export", "--output", str(output_file)])

        assert result.exit_code == 0
        assert output_file.exists()

        content = output_file.read_text(encoding="utf-8")
        assert "--- # PAPER: Large Language Models Survey ---" in content
        assert "--- # PAPER: Transformer Architecture Advances ---" in content
        assert "Paper content here." in content

    def test_export_no_processed_papers(self, temp_db, tmp_path, monkeypatch):
        from main import app
        from typer.testing import CliRunner

        runner = CliRunner()
        monkeypatch.setattr("main.DB_PATH", temp_db.db_path)

        output_file = tmp_path / "export.md"
        result = runner.invoke(app, ["export", "--output", str(output_file)])

        assert result.exit_code == 0
        assert "No processed papers to export." in result.output
