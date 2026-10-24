"""
Pinecone vector store interface for Cold Chain SOPs and compliance retrieval.
Lazy-loads Pinecone client so it never slows down Streamlit startup.
"""
from typing import List, Dict, Any
from src.config.settings import settings
from src.rag.embeddings import get_text_embedding

class VectorStoreService:
    def __init__(self):
        self._pc = None
        self._index = None
        self.index_name = settings.PINECONE_INDEX_NAME

    def _get_index(self):
        if self._index is None:
            if not settings.PINECONE_API_KEY:
                raise ValueError("PINECONE_API_KEY is not configured in .env")
            from pinecone import Pinecone
            self._pc = Pinecone(api_key=settings.PINECONE_API_KEY)
            self._index = self._pc.Index(self.index_name)
        return self._index

    def search_sops(self, query: str, top_k: int = 3) -> List[Dict[str, Any]]:
        if not settings.PINECONE_API_KEY:
            return [{"text": "Pinecone is not configured. Please supply PINECONE_API_KEY in .env."}]
        
        index = self._get_index()
        query_vector = get_text_embedding(query)
        response = index.query(vector=query_vector, top_k=top_k, include_metadata=True)

        results = []
        for match in response.get("matches", []):
            results.append({
                "score": match.get("score"),
                "text": match.get("metadata", {}).get("text", ""),
                "source": match.get("metadata", {}).get("source", "")
            })
        return results
