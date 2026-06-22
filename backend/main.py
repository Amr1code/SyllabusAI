from dotenv import load_dotenv

load_dotenv()

from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware

from backend.routes.chat import router as chat_router
from backend.routes.upload_syllabus import router as syllabus_router
from backend.routes.upload_textbook import router as textbook_router

app = FastAPI(title="SyllabusAI")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

app.include_router(syllabus_router)
app.include_router(textbook_router)
app.include_router(chat_router)
