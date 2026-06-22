import os

import chromadb

CHROMA_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "chroma_db")

_client = chromadb.PersistentClient(path=CHROMA_DIR)


def get_or_create_collection(session_id: str):
    return _client.get_or_create_collection(name=f"session_{session_id}")


def get_collection(session_id: str):
    return _client.get_collection(name=f"session_{session_id}")
