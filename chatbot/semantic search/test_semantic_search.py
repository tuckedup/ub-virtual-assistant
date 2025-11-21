import chromadb
from sentence_transformers import SentenceTransformer

# Load model + DB
model = SentenceTransformer("all-MiniLM-L6-v2")
client = chromadb.PersistentClient(path="chroma_db")
collection = client.get_collection("course_catalog")

def search(query):
    emb = model.encode([query]).tolist()
    return collection.query(query_embeddings=emb, n_results=3)

# Tests
print("\nQuery: machine learning courses")
print(search("machine learning"))

print("\nQuery: python basics")
print(search("python basics"))

print("\nQuery: clustering or unsupervised learning")
print(search("clustering unsupervised"))