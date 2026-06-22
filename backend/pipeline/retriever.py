from openai import OpenAI

from backend.storage.chroma_client import get_collection

client = OpenAI()


def retrieve_chunks(question: str, session_id: str, top_k: int = 5) -> list[str]:
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=[question],
    )
    query_embedding = response.data[0].embedding

    collection = get_collection(session_id)
    results = collection.query(
        query_embeddings=[query_embedding],
        n_results=top_k,
    )

    return results["documents"][0] if results["documents"] else []
