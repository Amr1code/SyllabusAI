import tiktoken

CHUNK_SIZE = 500
CHUNK_OVERLAP = 50

_enc = tiktoken.get_encoding("cl100k_base")


def chunk_text(text: str, session_id: str) -> list[dict]:
    words = text.split()
    tokens = _enc.encode(text)

    chunks = []
    start = 0
    chunk_index = 0

    while start < len(tokens):
        end = min(start + CHUNK_SIZE, len(tokens))
        chunk_tokens = tokens[start:end]
        chunk_text_str = _enc.decode(chunk_tokens)
        chunks.append({
            "text": chunk_text_str,
            "chunk_index": chunk_index,
            "session_id": session_id,
        })
        chunk_index += 1
        start += CHUNK_SIZE - CHUNK_OVERLAP

    return chunks
