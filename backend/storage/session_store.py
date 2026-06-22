import json
import os

SESSIONS_DIR = os.path.join(os.path.dirname(__file__), "..", "..", "sessions")


def _session_path(session_id: str) -> str:
    os.makedirs(SESSIONS_DIR, exist_ok=True)
    return os.path.join(SESSIONS_DIR, f"{session_id}.json")


def save_syllabus(session_id: str, syllabus_data: dict) -> None:
    path = _session_path(session_id)
    existing = {}
    if os.path.exists(path):
        with open(path, "r") as f:
            existing = json.load(f)
    existing["syllabus"] = syllabus_data
    with open(path, "w") as f:
        json.dump(existing, f, indent=2)


def load_syllabus(session_id: str) -> dict | None:
    path = _session_path(session_id)
    if not os.path.exists(path):
        return None
    with open(path, "r") as f:
        data = json.load(f)
    return data.get("syllabus")
