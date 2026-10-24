"""
Local Sentence-Transformers embedding provider.
Runs 100% locally on CPU without paid cloud API calls.
"""
from functools import lru_cache
from typing import List
from src.config.settings import settings

@lru_cache(maxsize=1)
def _get_model():
    from sentence_transformers import SentenceTransformer
    return SentenceTransformer(settings.EMBEDDING_MODEL_NAME)

def get_text_embedding(text: str) -> List[float]:
    model = _get_model()
    return model.encode(text).tolist()

def get_batch_embeddings(texts: List[str]) -> List[List[float]]:
    model = _get_model()
    return model.encode(texts).tolist()

