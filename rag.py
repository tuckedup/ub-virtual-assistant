# rag.py
"""
Lightweight RAG helper for UB chatbot.

Usage:
    from rag import query_rag
    context = query_rag("When does spring semester start?")
"""

from typing import List
from pathlib import Path

import chromadb
from chromadb.config import Settings
from sentence_transformers import SentenceTransformer


DB_PATH = "chroma_db"
COLLECTION_NAME = "ub_knowledge"

_client = chromadb.PersistentClient(path=DB_PATH, settings=Settings())
_collection = _client.get_or_create_collection(COLLECTION_NAME)

_model = SentenceTransformer("all-MiniLM-L6-v2")


def query_rag(question: str, k: int = 4) -> str:
    """
    Retrieve top-k relevant chunks from the UB knowledge index.
    Returns them as a single context string.
    """
    if not question.strip():
        return ""

    embedding = _model.encode([question], convert_to_numpy=True).tolist()[0]

    result = _collection.query(
        query_embeddings=[embedding],
        n_results=k,
    )

    docs: List[str] = result.get("documents", [[]])[0]
    if not docs:
        return ""

    # Join with spacing so the LLM can read it as context
    return "\n\n---\n\n".join(docs)
