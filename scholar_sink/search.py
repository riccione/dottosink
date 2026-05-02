from typing import Any, Dict, List

from sentence_transformers import SentenceTransformer


class PaperSearcher:
    def __init__(self, model_name: str = "all-MiniLM-L6-v2"):
        self.model = SentenceTransformer(model_name)
        self._cache: Dict[str, List[float]] = {}

    def generate_embedding(self, text: str) -> List[float]:
        if text in self._cache:
            return self._cache[text]

        embedding = self.model.encode(text).tolist()
        self._cache[text] = embedding
        return embedding

    def semantic_search(
        self,
        query: str,
        paper_embeddings: List[Dict[str, Any]],
        top_k: int = 5,
    ) -> List[Dict[str, Any]]:
        query_embedding = self.generate_embedding(query)

        results = []
        for item in paper_embeddings:
            score = self._cosine_similarity(query_embedding, item["embedding"])
            results.append({**item, "score": score})

        results.sort(key=lambda x: x["score"], reverse=True)
        return results[:top_k]

    @staticmethod
    def _cosine_similarity(vec1: List[float], vec2: List[float]) -> float:
        dot = sum(a * b for a, b in zip(vec1, vec2))
        mag1 = sum(a * a for a in vec1) ** 0.5
        mag2 = sum(b * b for b in vec2) ** 0.5
        if mag1 == 0 or mag2 == 0:
            return 0.0
        return dot / (mag1 * mag2)
