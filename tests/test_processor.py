import sys
from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from scholar_sink.processor import convert_pdf_to_md
from scholar_sink.db import DatabaseManager

sys.path.insert(0, str(Path(__file__).parent.parent))


@pytest.fixture
def temp_db(tmp_path):
    db_path = tmp_path / "test.db"
    return DatabaseManager(db_path)


@pytest.fixture
def temp_dirs(tmp_path):
    raw_dir = tmp_path / "raw"
    vault_dir = tmp_path / "vault"
    raw_dir.mkdir()
    vault_dir.mkdir()
    return raw_dir, vault_dir


@pytest.fixture
def fake_pdf(temp_dirs):
    raw_dir, _ = temp_dirs
    pdf_path = raw_dir / "2401.12345.pdf"
    pdf_path.write_bytes(b"%PDF-1.4 fake pdf content")
    return pdf_path


class TestConvertPdfToMd:
    def test_successful_conversion_creates_md_file(self, fake_pdf, temp_dirs):
        _, vault_dir = temp_dirs

        def mock_marker_write(pdf_path, md_path):
            md_path.write_text("# Test Paper\n\nConverted content", encoding="utf-8")

        with patch("scholar_sink.processor._convert_with_marker") as mock_marker:
            mock_marker.side_effect = mock_marker_write
            result = convert_pdf_to_md(fake_pdf, vault_dir)

        assert result == vault_dir / "2401.12345.md"
        assert result.exists()
        assert "Test Paper" in result.read_text()

    def test_marker_failure_falls_back_to_pymupdf(self, fake_pdf, temp_dirs):
        _, vault_dir = temp_dirs

        def mock_pymupdf_write(pdf_path, md_path):
            md_path.write_text("Fallback text", encoding="utf-8")

        with patch("scholar_sink.processor._convert_with_marker") as mock_marker:
            mock_marker.side_effect = Exception("OOM error")
            with patch("scholar_sink.processor._convert_with_pymupdf") as mock_pymupdf:
                mock_pymupdf.side_effect = mock_pymupdf_write
                result = convert_pdf_to_md(fake_pdf, vault_dir)

        mock_marker.assert_called_once()
        mock_pymupdf.assert_called_once()
        assert result == vault_dir / "2401.12345.md"
        assert result.exists()

    def test_both_conversions_fail_raises_error(self, fake_pdf, temp_dirs):
        _, vault_dir = temp_dirs

        with patch("scholar_sink.processor._convert_with_marker") as mock_marker:
            mock_marker.side_effect = Exception("OOM error")
            with patch("scholar_sink.processor._convert_with_pymupdf") as mock_pymupdf:
                mock_pymupdf.side_effect = Exception("PyMuPDF error")
                with pytest.raises(Exception):
                    convert_pdf_to_md(fake_pdf, vault_dir)


class TestProcessCommandIntegration:
    def test_successful_process_updates_db_with_md_path_and_processed_status(
        self, fake_pdf, temp_dirs, temp_db, monkeypatch
    ):
        _, vault_dir = temp_dirs

        paper_data = {
            "arxiv_id": "2401.12345",
            "title": "Test Paper",
            "authors": "['Author']",
            "published": "2024-01-01",
            "summary": "Test summary",
            "pdf_path": str(fake_pdf),
            "md_path": None,
            "status": "downloaded",
        }
        temp_db.insert_paper(paper_data)

        def mock_marker_write(pdf_path, md_path):
            md_path.write_text("# Test Paper\n\nConverted content", encoding="utf-8")

        monkeypatch.setattr("scholar_sink.processor._convert_with_marker", mock_marker_write)

        from main import app
        from typer.testing import CliRunner

        runner = CliRunner()
        monkeypatch.setattr("main.DB_PATH", temp_db.db_path)
        monkeypatch.setattr("main.VAULT_DIR", vault_dir)
        monkeypatch.setattr("main.RAW_DIR", fake_pdf.parent)

        result = runner.invoke(app, ["process"])
        assert result.exit_code == 0

        updated = temp_db.get_paper_by_id("2401.12345")
        assert updated["status"] == "processed"
        assert updated["md_path"] is not None
        assert Path(updated["md_path"]).exists()

    def test_failed_process_updates_db_status_to_failed(
        self, fake_pdf, temp_dirs, temp_db, monkeypatch
    ):
        _, vault_dir = temp_dirs

        paper_data = {
            "arxiv_id": "2401.12345",
            "title": "Test Paper",
            "authors": "['Author']",
            "published": "2024-01-01",
            "summary": "Test summary",
            "pdf_path": str(fake_pdf),
            "md_path": None,
            "status": "downloaded",
        }
        temp_db.insert_paper(paper_data)

        def mock_converter_fail(*args, **kwargs):
            raise Exception("Conversion failed")

        monkeypatch.setattr("scholar_sink.processor._convert_with_marker", mock_converter_fail)
        monkeypatch.setattr("scholar_sink.processor._convert_with_pymupdf", mock_converter_fail)

        from main import app
        from typer.testing import CliRunner

        runner = CliRunner()
        monkeypatch.setattr("main.DB_PATH", temp_db.db_path)
        monkeypatch.setattr("main.VAULT_DIR", vault_dir)
        monkeypatch.setattr("main.RAW_DIR", fake_pdf.parent)

        result = runner.invoke(app, ["process"])
        assert result.exit_code == 0

        updated = temp_db.get_paper_by_id("2401.12345")
        assert updated["status"] == "failed"

    def test_missing_pdf_skips_paper(self, temp_dirs, temp_db, monkeypatch):
        _, vault_dir = temp_dirs

        paper_data = {
            "arxiv_id": "2401.12345",
            "title": "Test Paper",
            "authors": "['Author']",
            "published": "2024-01-01",
            "summary": "Test summary",
            "pdf_path": "/nonexistent/file.pdf",
            "md_path": None,
            "status": "downloaded",
        }
        temp_db.insert_paper(paper_data)

        from main import app
        from typer.testing import CliRunner

        runner = CliRunner()
        monkeypatch.setattr("main.DB_PATH", temp_db.db_path)
        monkeypatch.setattr("main.VAULT_DIR", vault_dir)

        result = runner.invoke(app, ["process"])
        assert result.exit_code == 0

        updated = temp_db.get_paper_by_id("2401.12345")
        assert updated["status"] == "downloaded"
