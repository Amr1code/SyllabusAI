from fastapi import APIRouter, File, Form, UploadFile

from backend.pipeline.chunker import chunk_text
from backend.pipeline.embedder import embed_and_store
from backend.pipeline.pdf_parser import extract_text_from_pdf

router = APIRouter()


@router.post("/upload-textbook")
async def upload_textbook(file: UploadFile = File(...), session_id: str = Form(...)):
    pdf_bytes = await file.read()
    raw_text = extract_text_from_pdf(pdf_bytes)
    chunks = chunk_text(raw_text, session_id)
    num_stored = embed_and_store(chunks, session_id)
    return {
        "status": "success",
        "chunks_stored": num_stored,
    }
