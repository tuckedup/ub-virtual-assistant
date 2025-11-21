import chromadb
from sentence_transformers import SentenceTransformer

# Load the embedding model
embedder = SentenceTransformer("all-MiniLM-L6-v2")

# Load Chroma collection
client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_collection("course_catalog")

def retrieve_courses(query, k=5):
    """Returns top-k most relevant courses from Chroma."""
    query_emb = embedder.encode([query]).tolist()
    results = collection.query(
        query_embeddings=query_emb,
        n_results=k
    )
    return results
