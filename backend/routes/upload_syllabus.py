from fastapi import APIRouter, File, Form, HTTPException, UploadFile

from backend.pipeline.pdf_parser import extract_text_from_pdf
from backend.pipeline.syllabus_extractor import extract_syllabus
from backend.storage.session_store import save_syllabus

router = APIRouter()


@router.post("/upload-syllabus")
async def upload_syllabus(file: UploadFile = File(...), session_id: str = Form(...)):
    if not session_id or not session_id.strip():
        raise HTTPException(status_code=400, detail="session_id is required.")

    pdf_bytes = await file.read()
    if not pdf_bytes:
        raise HTTPException(status_code=400, detail="Uploaded file is empty.")

    raw_text = extract_text_from_pdf(pdf_bytes)
    if not raw_text.strip():
        raise HTTPException(status_code=400, detail="Could not extract text from the PDF.")

    syllabus_data = extract_syllabus(raw_text)
    save_syllabus(session_id, syllabus_data)
    return {
        "status": "success",
        "course_name": syllabus_data.get("course_name", ""),
        "topics_covered": syllabus_data.get("topics_covered", []),
    }
