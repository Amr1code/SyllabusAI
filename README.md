# SyllabusAI

A RAG-powered (Retrieval-Augmented Generation) AI tutoring agent. Students upload their course syllabus and textbook as PDFs, then ask questions in a chat interface. The agent **only** answers questions about topics listed in the syllabus, using **only** content retrieved from the textbook — it never draws on outside knowledge.

## How It Works

1. **Upload a syllabus** — The PDF is parsed and sent to GPT-4o, which extracts structured data: course name, professor, topics covered, weekly schedule, and textbook title.
2. **Upload a textbook** — The PDF is parsed, split into 500-token chunks (with 50-token overlap), embedded with `text-embedding-3-small`, and stored in a Chroma vector database.
3. **Ask a question** — The agent first checks whether the question is related to a syllabus topic using embedding cosine similarity. If the topic is out of scope, it refuses. If in scope, it retrieves the 5 most relevant textbook chunks and sends them alongside a strict system prompt to GPT-4o, which generates an answer grounded entirely in the provided context.

## Demo
<img width="1911" height="947" alt="Image" src="https://github.com/user-attachments/assets/94956b46-a3f3-447e-b56d-b9961edb4a2e" />

<img width="1913" height="951" alt="Image" src="https://github.com/user-attachments/assets/751b8305-63cc-4b6c-a473-fbbba2ccc694" />

<img width="1916" height="951" alt="Image" src="https://github.com/user-attachments/assets/9303e377-cae1-43a0-b0e2-a44e7fd97b61" />
-When a user asks for something that isn't in the content or syllabus:
<img width="1916" height="951" alt="Image" src="https://github.com/user-attachments/assets/2180a3f4-87bc-49d5-b824-ddf7bdde8019" />

## Architecture

```
Streamlit (frontend)  ──HTTP──>  FastAPI (backend)
                                    │
                    ┌───────────────┼───────────────┐
                    │               │               │
              /upload-syllabus  /upload-textbook   /chat
                    │               │               │
               PDF Parser      PDF Parser      Topic Check (embeddings)
                    │               │               │
            Syllabus Extractor  Chunker         Retriever (Chroma)
               (GPT-4o)            │               │
                    │           Embedder        Prompt Builder
               Session Store   (text-embedding     │
              (JSON files)      -3-small)       GPT-4o → Answer
                                    │
                                Chroma DB
```

Each browser session gets a unique `session_id` (UUID). This ID namespaces both the Chroma collection and the session JSON file, so multiple students can use the app simultaneously without interference.

## Project Structure

```
├── frontend/
│   └── app.py                     # Streamlit UI
├── backend/
│   ├── main.py                    # FastAPI app entry point
│   ├── routes/
│   │   ├── upload_syllabus.py     # POST /upload-syllabus
│   │   ├── upload_textbook.py     # POST /upload-textbook
│   │   └── chat.py                # POST /chat
│   ├── pipeline/
│   │   ├── pdf_parser.py          # PyMuPDF: PDF bytes → text
│   │   ├── syllabus_extractor.py  # GPT-4o: text → structured JSON
│   │   ├── chunker.py             # Token-based text chunking
│   │   ├── embedder.py            # Embed chunks → store in Chroma
│   │   └── retriever.py           # Query Chroma → top-5 chunks
│   ├── prompt/
│   │   └── builder.py             # Assemble system prompt + context
│   └── storage/
│       ├── chroma_client.py       # Chroma DB setup, per-session collections
│       └── session_store.py       # Save/load syllabus JSON per session
├── .env                           # OPENAI_API_KEY (not committed)
└── requirements.txt
```

## Setup

### Prerequisites

- Python 3.10+
- An OpenAI API key

### Installation

```bash
pip install -r requirements.txt
```

Create a `.env` file in the project root:

```
OPENAI_API_KEY=your_key_here
```

### Running

Start both services in separate terminals:

```bash
# Terminal 1 — Backend (port 8000)
uvicorn backend.main:app --reload

# Terminal 2 — Frontend (port 8501)
streamlit run frontend/app.py
```

Open http://localhost:8501 in your browser.

## Usage

1. In the sidebar, upload your **syllabus PDF** — the app will extract and display the detected topics.
2. Upload your **textbook PDF** — this may take a minute for large files as it chunks and embeds the content.
3. Start asking questions in the chat. The agent will:
   - Answer from the textbook if the topic is in the syllabus
   - Respond with "That topic is not in your course material" if the topic is outside the syllabus
   - Respond with "That's not covered in your course material" if the topic is in the syllabus but not found in the textbook

## Tech Stack

| Layer | Tool |
|---|---|
| Frontend | Streamlit |
| Backend | FastAPI |
| PDF Parsing | PyMuPDF (`fitz`) |
| Syllabus Extraction | OpenAI GPT-4o |
| Embeddings | OpenAI `text-embedding-3-small` |
| Vector Database | ChromaDB (local, persistent) |
| Text Chunking | tiktoken (`cl100k_base` encoding) |
| Student Q&A | OpenAI GPT-4o |

## API Endpoints

### `POST /upload-syllabus`
- **Body**: multipart form — `file` (PDF), `session_id` (string)
- **Returns**: `{ status, course_name, topics_covered }`

### `POST /upload-textbook`
- **Body**: multipart form — `file` (PDF), `session_id` (string)
- **Returns**: `{ status, chunks_stored }`

### `POST /chat`
- **Body**: JSON — `{ session_id, question }`
- **Returns**: `{ answer }`
