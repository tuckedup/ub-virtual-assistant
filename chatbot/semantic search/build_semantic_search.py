import json
import chromadb
from sentence_transformers import SentenceTransformer

model = SentenceTransformer("all-MiniLM-L6-v2")

with open("courses.json") as f:
    courses = json.load(f)

client = chromadb.PersistentClient(path="chroma_db")

collection = client.get_or_create_collection(
    name="course_catalog",
    metadata={"hnsw:space": "cosine"}
)

documents = []
ids = []
metadatas = []

for c in courses:
    # Convert list fields to strings
    prereq_str = ", ".join(c["prerequisites"]) if isinstance(c["prerequisites"], list) else c["prerequisites"]
    semester_str = ", ".join(c["semester"]) if isinstance(c["semester"], list) else c["semester"]

    text = (
        f"{c['title']}. "
        f"{c['description']}. "
        f"Prerequisites: {prereq_str or 'None'}."
    )

    documents.append(text)
    ids.append(c["course_id"])

    # Metadata must contain ONLY primitive types
    metadatas.append({
        "course_id": c["course_id"],
        "title": c["title"],
        "prerequisites": prereq_str,
        "credits": c["credits"],
        "department": c["department"],
        "semester": semester_str,
        "instructor": c["instructor"]
    })

embeddings = model.encode(documents).tolist()

collection.add(
    documents=documents,
    embeddings=embeddings,
    ids=ids,
    metadatas=metadatas
)

print("Course RAG index created successfully.")
print(f"Indexed {len(documents)} courses into Chroma.")

