from rag_pipeline import rag_answer

while True:
    q = input("\nAsk a course question: ")
    print("\nBot:", rag_answer(q))
