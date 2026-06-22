import io
import zipfile

from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from backend.pipeline.chunker import chunk_text
from backend.pipeline.embedder import embed_and_store
from backend.pipeline.pdf_parser import extract_text_from_pdf

router = APIRouter()


def _process_pdf(pdf_bytes: bytes, filename: str, session_id: str) -> dict:
    raw_text = extract_text_from_pdf(pdf_bytes)
    if not raw_text.strip():
        return {"filename": filename, "status": "skipped", "detail": "No text extracted", "chunks_stored": 0}

    chunks = chunk_text(raw_text, session_id)
    if not chunks:
        return {"filename": filename, "status": "skipped", "detail": "No chunks created", "chunks_stored": 0}

    num_stored = embed_and_store(chunks, session_id)
    return {"filename": filename, "status": "success", "chunks_stored": num_stored}


@router.post("/upload-textbook")
async def upload_textbook(
    files: list[UploadFile] = File(...),
    session_id: str = Form(...),
):
    if not session_id or not session_id.strip():
        raise HTTPException(status_code=400, detail="session_id is required.")

    results = []
    total_chunks = 0

    for uploaded_file in files:
        file_bytes = await uploaded_file.read()
        if not file_bytes:
            results.append({"filename": uploaded_file.filename, "status": "skipped", "detail": "Empty file", "chunks_stored": 0})
            continue

        if uploaded_file.filename.lower().endswith(".zip"):
            try:
                with zipfile.ZipFile(io.BytesIO(file_bytes)) as zf:
                    pdf_names = [n for n in zf.namelist() if n.lower().endswith(".pdf") and not n.startswith("__MACOSX")]
                    if not pdf_names:
                        results.append({"filename": uploaded_file.filename, "status": "skipped", "detail": "No PDFs found in zip", "chunks_stored": 0})
                        continue
                    for pdf_name in sorted(pdf_names):
                        pdf_bytes = zf.read(pdf_name)
                        result = _process_pdf(pdf_bytes, pdf_name, session_id)
                        total_chunks += result["chunks_stored"]
                        results.append(result)
            except zipfile.BadZipFile:
                results.append({"filename": uploaded_file.filename, "status": "error", "detail": "Invalid zip file", "chunks_stored": 0})
        elif uploaded_file.filename.lower().endswith(".pdf"):
            result = _process_pdf(file_bytes, uploaded_file.filename, session_id)
            total_chunks += result["chunks_stored"]
            results.append(result)
        else:
            results.append({"filename": uploaded_file.filename, "status": "skipped", "detail": "Unsupported file type (PDF or ZIP only)", "chunks_stored": 0})

    if total_chunks == 0:
        raise HTTPException(status_code=400, detail="No text could be extracted from any of the uploaded files.")

    return {
        "status": "success",
        "total_chunks_stored": total_chunks,
        "files": results,
    }
