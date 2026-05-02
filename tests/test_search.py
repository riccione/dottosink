import sys
from pathlib import Path
from unittest.mock import patch

import pytest

from scholar_sink.search import PaperSearcher
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
            "title": "Deep Learning Advances",
            "authors": "['Author One']",
            "published": "2024-01-01",
            "summary": "This paper discusses neural networks and deep learning architectures for computer vision.",
            "pdf_path": "/tmp/2401.12345.pdf",
            "md_path": "/tmp/vault/2401.12345.md",
            "status": "processed",
        },
        {
            "arxiv_id": "2402.54321",
            "title": "Fluid Dynamics Study",
            "authors": "['Author Two']",
            "published": "2024-02-15",
            "summary": "This paper studies fluid dynamics and turbulence in pipe flows.",
            "pdf_path": "/tmp/2402.54321.pdf",
            "md_path": "/tmp/vault/2402.54321.md",
            "status": "processed",
        },
    ]
    for p in papers:
        temp_db.insert_paper(p)

    return temp_db


class TestSimilarity:
    def test_neural_networks_ranks_deep_learning_higher(self, populated_db):
        # Deep learning embedding is closer to query
        deep_learning_emb = [0.9, 0.1, 0.8, 0.7, 0.6]
        fluid_dynamics_emb = [0.1, 0.9, 0.2, 0.3, 0.4]
        query_emb = [0.85, 0.15, 0.75, 0.65, 0.55]

        paper_embeddings = [
            {
                "arxiv_id": "2401.12345",
                "embedding": deep_learning_emb,
                "paper": populated_db.get_paper_by_id("2401.12345"),
            },
            {
                "arxiv_id": "2402.54321",
                "embedding": fluid_dynamics_emb,
                "paper": populated_db.get_paper_by_id("2402.54321"),
            },
        ]

        with patch.object(PaperSearcher, "generate_embedding", return_value=query_emb):
            searcher = PaperSearcher()
            results = searcher.semantic_search(
                "neural networks", paper_embeddings, top_k=5
            )

        assert results[0]["paper"]["arxiv_id"] == "2401.12345"
        assert results[1]["paper"]["arxiv_id"] == "2402.54321"
        assert results[0]["score"] > results[1]["score"]


class TestPersistence:
    def test_embedding_saved_and_loaded(self, temp_db):
        temp_db.insert_paper(
            {
                "arxiv_id": "2401.12345",
                "title": "Test Paper",
                "authors": "['Author']",
                "published": "2024-01-01",
                "summary": "Test summary about neural networks.",
                "pdf_path": "/tmp/test.pdf",
                "md_path": "/tmp/vault/test.md",
                "status": "processed",
            }
        )

        test_embedding = [0.1, 0.2, 0.3, 0.4, 0.5]

        with patch.object(
            PaperSearcher, "generate_embedding", return_value=test_embedding
        ):
            searcher = PaperSearcher()
            embedding = searcher.generate_embedding("Test summary.")
            temp_db.store_embedding("2401.12345", embedding)

        retrieved = temp_db.get_all_embeddings()
        assert len(retrieved) == 1
        assert retrieved[0]["arxiv_id"] == "2401.12345"
        assert retrieved[0]["embedding"] == test_embedding
