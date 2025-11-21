# build_rag_index.py
"""
Builds a small vector index from your existing UB JSON knowledge:
- data/academic_info.json
- data/campus_services.json
- data/faqs.json
- data/departments.json

Run once (or whenever data changes):
    python build_rag_index.py
"""

import json
from pathlib import Path
from sentence_transformers import SentenceTransformer
import chromadb
from chromadb.config import Settings


# --------- 1. Setup Chroma and embedding model ---------

DB_PATH = "chroma_db"  # folder will be created
COLLECTION_NAME = "ub_knowledge"

client = chromadb.PersistentClient(path=DB_PATH, settings=Settings())
collection = client.get_or_create_collection(COLLECTION_NAME)

model = SentenceTransformer("all-MiniLM-L6-v2")


# --------- 2. Helpers to flatten JSON into text docs ---------

DATA_DIR = Path("data")

FILES = [
    "academic_info.json",
    "campus_services.json",
    "faqs.json",
    "departments.json",
]


def load_json(filename: str):
    path = DATA_DIR / filename
    if not path.exists():
        print(f"[WARN] {path} not found, skipping.")
        return {}
    with path.open("r", encoding="utf-8") as f:
        return json.load(f)


def dict_to_text(d: dict, prefix: str = "") -> str:
    """
    Turn a nested dict into readable bullet-style text.
    """
    lines = []

    for key, value in d.items():
        key_str = key.replace("_", " ").title()
        if isinstance(value, str):
            lines.append(f"{prefix}{key_str}: {value}")
        elif isinstance(value, (int, float, bool)):
            lines.append(f"{prefix}{key_str}: {value}")
        elif isinstance(value, dict):
            lines.append(f"{prefix}{key_str}:")
            lines.append(dict_to_text(value, prefix + "  "))
        elif isinstance(value, list):
            lines.append(f"{prefix}{key_str}:")
            for item in value:
                if isinstance(item, dict):
                    lines.append(dict_to_text(item, prefix + "  - "))
                else:
                    lines.append(f"{prefix}  - {item}")
    return "\n".join(lines)


def build_documents():
    """
    Build a list of (id, text, metadata) tuples from JSON files.
    """
    docs = []

    for fname in FILES:
        data = load_json(fname)
        if not data:
            continue

        # top-level keys become separate docs
        for top_key, value in data.items():
            text = dict_to_text(value)
            if not text.strip():
                continue

            doc_id = f"{fname}:{top_key}"
            metadata = {
                "source_file": fname,
                "section": top_key,
            }
            docs.append((doc_id, text, metadata))

    return docs


# --------- 3. Build and store in Chroma ---------

def main():
    docs = build_documents()
    if not docs:
        print("No docs found to index.")
        return

    ids = [d[0] for d in docs]
    texts = [d[1] for d in docs]
    metadatas = [d[2] for d in docs]

    print(f"Indexing {len(texts)} documents into Chroma collection '{COLLECTION_NAME}'...")

    embeddings = model.encode(texts, convert_to_numpy=True).tolist()

    # Clear old collection (optional) then add
    collection.delete(where={})  # wipe existing
    collection.add(
        ids=ids,
        documents=texts,
        metadatas=metadatas,
        embeddings=embeddings,
    )

    print("Done. RAG index built at", DB_PATH)


if __name__ == "__main__":
    main()
