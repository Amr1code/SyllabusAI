from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from backend.pipeline.chunker import chunk_text
from backend.pipeline.embedder import embed_and_store
from backend.pipeline.pdf_parser import extract_text_from_pdf

router = APIRouter()


@router.post("/upload-textbook")
async def upload_textbook(file: UploadFile = File(...), session_id: str = Form(...)):
    if not session_id or not session_id.strip():
        raise HTTPException(status_code=400, detail="session_id is required.")

    pdf_bytes = await file.read()
    if not pdf_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    raw_text = extract_text_from_pdf(pdf_bytes)
    if not raw_text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from the PDF.")

    chunks = chunk_text(raw_text, session_id)
    if not chunks:
        raise HTTPException(status_code=400, detail="No text chunks could be created from the PDF.")

    num_stored = embed_and_store(chunks, session_id)
    return {
        "status": "success",
        "chunks_stored": num_stored,
    }
