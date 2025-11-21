import chromadb
from sentence_transformers import SentenceTransformer

# 1. Load embedding model
model = SentenceTransformer("all-MiniLM-L6-v2")

# 2. Initialize Chroma (local DB folder)
client = chromadb.PersistentClient(path="chroma_test_db")

# 3. Create collection
collection = client.get_or_create_collection(
    name="test_courses",
    metadata={"hnsw:space": "cosine"}
)

# 4. Sample documents
documents = [
    "Machine learning course covering supervised and unsupervised learning.",
    "Introduction to Python programming with loops and functions.",
    "Advanced data mining with clustering and association rules.",
    "Algorithms course with greedy algorithms and dynamic programming."
]

ids = ["C1", "C2", "C3", "C4"]

# 5. Compute embeddings
embeddings = model.encode(documents).tolist()

# 6. Insert into Chroma
collection.add(
    documents=documents,
    embeddings=embeddings,
    ids=ids
)

print("Chroma DB setup complete.\n")

# 7. Test queries
def query(text):
    emb = model.encode([text]).tolist()
    results = collection.query(
        query_embeddings=emb,
        n_results=2
    )
    return results

# Test 1
print("Query: 'clustering'")
print(query("clustering"))

# Test 2
print("\nQuery: 'python basics'")
print(query("python basics"))

# Test 3
print("\nQuery: 'dynamic programming'")
print(query("dynamic programming"))
