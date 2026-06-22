from openai import OpenAI

from backend.storage.chroma_client import get_or_create_collection

client = OpenAI()


def embed_and_store(chunks: list[dict], session_id: str) -> int:
    collection = get_or_create_collection(session_id)

    texts = [c["text"] for c in chunks]
    response = client.embeddings.create(
        model="text-embedding-3-small",
        input=texts,
    )

    embeddings = [item.embedding for item in response.data]
    ids = [f"{session_id}_chunk_{c['chunk_index']}" for c in chunks]
    metadatas = [{"chunk_index": c["chunk_index"], "session_id": c["session_id"]} for c in chunks]

    collection.add(
        ids=ids,
        embeddings=embeddings,
        documents=texts,
        metadatas=metadatas,
    )

    return len(chunks)
