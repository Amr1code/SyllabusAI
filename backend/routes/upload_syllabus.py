from fastapi import APIRouter, File, Form, UploadFile

from backend.pipeline.pdf_parser import extract_text_from_pdf
from backend.pipeline.syllabus_extractor import extract_syllabus
from backend.storage.session_store import save_syllabus

router = APIRouter()


@router.post("/upload-syllabus")
async def upload_syllabus(file: UploadFile = File(...), session_id: str = Form(...)):
    pdf_bytes = await file.read()
    raw_text = extract_text_from_pdf(pdf_bytes)
    syllabus_data = extract_syllabus(raw_text)
    save_syllabus(session_id, syllabus_data)
    return {
        "status": "success",
        "course_name": syllabus_data.get("course_name", ""),
        "topics_covered": syllabus_data.get("topics_covered", []),
    }
