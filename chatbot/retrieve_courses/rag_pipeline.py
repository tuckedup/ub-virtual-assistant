import ollama
from retriever import retrieve_courses

def rag_answer(query):
    retrieved = retrieve_courses(query, k=3)

    context = ""
    for doc, meta in zip(retrieved["documents"][0], retrieved["metadatas"][0]):
        context += f"COURSE: {meta['course_id']} - {meta['title']}\n"
        context += f"{doc}\n"
        context += f"Metadata: {meta}\n\n"

    prompt = f"""
Answer the question using ONLY this context:

{context}

Question: {query}
"""

    response = ollama.generate(
        model="mistral",
        prompt=prompt
    )
    
    return response["response"]
