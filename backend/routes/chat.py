from fastapi import APIRouter, HTTPException
from openai import OpenAI
from pydantic import BaseModel

from backend.pipeline.retriever import retrieve_chunks
from backend.prompt.builder import build_prompt
from backend.storage.session_store import load_syllabus

router = APIRouter()
client = OpenAI()


class ChatRequest(BaseModel):
    session_id: str
    question: str


@router.post("/chat")
async def chat(req: ChatRequest):
    if not req.session_id or not req.session_id.strip():
        raise HTTPException(status_code=400, detail="session_id is required.")
    if not req.question or not req.question.strip():
        raise HTTPException(status_code=400, detail="question is required.")

    syllabus = load_syllabus(req.session_id)
    if not syllabus:
        raise HTTPException(status_code=400, detail="Syllabus not uploaded yet for this session.")

    topics = syllabus.get("topics_covered", [])
    if not topics:
        raise HTTPException(status_code=400, detail="No topics found in syllabus. Please re-upload.")

    topic_check = client.embeddings.create(
        model="text-embedding-3-small",
        input=[req.question] + topics,
    )
    question_emb = topic_check.data[0].embedding
    max_similarity = 0.0
    for i, topic in enumerate(topics):
        topic_emb = topic_check.data[i + 1].embedding
        dot = sum(a * b for a, b in zip(question_emb, topic_emb))
        mag_q = sum(a * a for a in question_emb) ** 0.5
        mag_t = sum(a * a for a in topic_emb) ** 0.5
        if mag_q > 0 and mag_t > 0:
            similarity = dot / (mag_q * mag_t)
            max_similarity = max(max_similarity, similarity)

    if max_similarity < 0.3:
        return {"answer": "That topic is not in your course material."}

    try:
        chunks = retrieve_chunks(req.question, req.session_id)
    except Exception:
        raise HTTPException(status_code=400, detail="Textbook not uploaded yet for this session.")

    course_name = syllabus.get("course_name", "")
    messages = build_prompt(topics, chunks, req.question, course_name)
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=messages,
        temperature=0,
    )

    return {"answer": response.choices[0].message.content}
