from pathlib import Path
from unittest.mock import Mock, patch

import pytest

from scholar_sink.models import Paper
from scholar_sink.fetcher import search_arxiv, download_pdf
from scholar_sink.db import DatabaseManager


@pytest.fixture
def mock_arxiv_result():
    result = Mock()
    result.entry_id = "http://arxiv.org/abs/2401.12345"
    result.title = "Test Paper Title"
    author1 = Mock()
    author1.name = "Author One"
    author2 = Mock()
    author2.name = "Author Two"
    result.authors = [author1, author2]
    result.published = Mock(isoformat=Mock(return_value="2024-01-01T00:00:00"))
    result.summary = "This is a test paper summary."
    return result


@pytest.fixture
def temp_db(tmp_path):
    db_path = tmp_path / "test.db"
    return DatabaseManager(db_path)


class TestSearchArxiv:
    @patch("scholar_sink.fetcher.arxiv.Client")
    def test_search_returns_papers(self, mock_client, mock_arxiv_result):
        mock_instance = Mock()
        mock_instance.results.return_value = [mock_arxiv_result]
        mock_client.return_value = mock_instance

        papers = search_arxiv("test query", 1)

        assert len(papers) == 1
        assert papers[0].arxiv_id == "2401.12345"
        assert papers[0].title == "Test Paper Title"

    @patch("scholar_sink.fetcher.arxiv.Client")
    def test_search_maps_fields_correctly(self, mock_client, mock_arxiv_result):
        mock_instance = Mock()
        mock_instance.results.return_value = [mock_arxiv_result]
        mock_client.return_value = mock_instance

        papers = search_arxiv("test", 1)

        assert papers[0].authors == ["Author One", "Author Two"]
        assert papers[0].summary == "This is a test paper summary."


class TestDownloadPdf:
    @patch("scholar_sink.fetcher.requests.get")
    @patch("scholar_sink.fetcher.time.sleep")
    def test_download_calls_sleep(self, mock_sleep, mock_get, tmp_path):
        mock_response = Mock()
        mock_response.raise_for_status = Mock()
        mock_response.content = b"fake pdf content"
        mock_get.return_value = mock_response

        paper = Paper(
            arxiv_id="2401.12345",
            title="Test",
            authors=["A"],
            published="2024-01-01",
            summary="Test",
        )

        result = download_pdf(paper, tmp_path)

        assert result is not None
        mock_sleep.assert_called_once_with(3)

    @patch("scholar_sink.fetcher.requests.get")
    @patch("scholar_sink.fetcher.time.sleep")
    def test_rate_limit_error(self, mock_sleep, mock_get):
        mock_response = Mock()
        mock_response.status_code = 429
        mock_response.raise_for_status.side_effect = Exception("429 error")
        mock_get.return_value = mock_response

        paper = Paper(
            arxiv_id="2401.12345",
            title="Test",
            authors=["A"],
            published="2024-01-01",
            summary="Test",
        )

        with pytest.raises(Exception, match="429"):
            download_pdf(paper, Path("/tmp"))

    @patch("scholar_sink.fetcher.time.sleep")
    def test_deduplication_existing_file(self, mock_sleep, tmp_path):
        paper = Paper(
            arxiv_id="2401.12345",
            title="Test",
            authors=["A"],
            published="2024-01-01",
            summary="Test",
        )

        raw_dir = tmp_path / "raw"
        raw_dir.mkdir()
        pdf_path = raw_dir / "2401.12345.pdf"
        pdf_path.write_bytes(b"existing content")

        result = download_pdf(paper, raw_dir)

        assert result == pdf_path
        mock_sleep.assert_called_once_with(3)


class TestDatabaseDeduplication:
    def test_duplicate_arxiv_id_skipped(self, temp_db):
        paper_data = {
            "arxiv_id": "2401.12345",
            "title": "Test",
            "authors": "['A']",
            "published": "2024-01-01",
            "summary": "Test",
            "pdf_path": "/tmp/test.pdf",
            "md_path": None,
            "status": "downloaded",
        }

        temp_db.insert_paper(paper_data)
        assert temp_db.paper_exists("2401.12345")

        # Second insert should not raise
        temp_db.insert_paper(paper_data)
        papers = temp_db.get_all_papers()
        assert len(papers) == 1
