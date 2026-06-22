import uuid

import requests
import streamlit as st

API_URL = "http://localhost:8000"

st.set_page_config(page_title="SyllabusAI", layout="wide")

if "session_id" not in st.session_state:
    st.session_state.session_id = str(uuid.uuid4())
if "messages" not in st.session_state:
    st.session_state.messages = []
if "syllabus_uploaded" not in st.session_state:
    st.session_state.syllabus_uploaded = False
if "textbook_uploaded" not in st.session_state:
    st.session_state.textbook_uploaded = False
if "topics" not in st.session_state:
    st.session_state.topics = []
if "course_name" not in st.session_state:
    st.session_state.course_name = ""

with st.sidebar:
    st.header("Upload Course Materials")

    st.subheader("1. Syllabus")
    syllabus_file = st.file_uploader("Upload your syllabus (PDF)", type=["pdf"], key="syllabus")
    if syllabus_file and not st.session_state.syllabus_uploaded:
        with st.spinner("Processing syllabus..."):
            resp = requests.post(
                f"{API_URL}/upload-syllabus",
                files={"file": (syllabus_file.name, syllabus_file.getvalue(), "application/pdf")},
                data={"session_id": st.session_state.session_id},
            )
        if resp.status_code == 200:
            result = resp.json()
            st.session_state.syllabus_uploaded = True
            st.session_state.topics = result.get("topics_covered", [])
            st.session_state.course_name = result.get("course_name", "")
            st.success(f"Syllabus uploaded: {result.get('course_name', 'Unknown Course')}")
        else:
            st.error(f"Error: {resp.text}")

    st.subheader("2. Textbook")
    textbook_files = st.file_uploader(
        "Upload your textbook (PDFs or ZIP of PDFs)",
        type=["pdf", "zip"],
        accept_multiple_files=True,
        key="textbook",
    )
    if textbook_files and not st.session_state.textbook_uploaded:
        with st.spinner("Processing textbook files (this may take a minute)..."):
            upload_files = [
                ("files", (f.name, f.getvalue(), "application/octet-stream"))
                for f in textbook_files
            ]
            resp = requests.post(
                f"{API_URL}/upload-textbook",
                files=upload_files,
                data={"session_id": st.session_state.session_id},
            )
        if resp.status_code == 200:
            result = resp.json()
            st.session_state.textbook_uploaded = True
            total = result.get("total_chunks_stored", 0)
            file_results = result.get("files", [])
            st.success(f"Textbook uploaded: {total} chunks indexed from {len(file_results)} file(s)")
            for fr in file_results:
                if fr["status"] == "success":
                    st.caption(f"  {fr['filename']}: {fr['chunks_stored']} chunks")
                else:
                    st.caption(f"  {fr['filename']}: {fr.get('detail', 'skipped')}")
        else:
            st.error(f"Error: {resp.text}")

    if st.session_state.topics:
        st.subheader("Topics in your syllabus")
        for topic in st.session_state.topics:
            st.write(f"- {topic}")

if st.session_state.course_name:
    st.title(f"Tutor: {st.session_state.course_name}")
else:
    st.title("SyllabusAI")

if not st.session_state.syllabus_uploaded or not st.session_state.textbook_uploaded:
    missing = []
    if not st.session_state.syllabus_uploaded:
        missing.append("syllabus")
    if not st.session_state.textbook_uploaded:
        missing.append("textbook")
    st.info(f"Please upload your {' and '.join(missing)} in the sidebar to start chatting.")

for msg in st.session_state.messages:
    with st.chat_message(msg["role"]):
        st.write(msg["content"])

if prompt := st.chat_input("Ask a question about your course..."):
    if not st.session_state.syllabus_uploaded or not st.session_state.textbook_uploaded:
        st.warning("Please upload both your syllabus and textbook first.")
    else:
        st.session_state.messages.append({"role": "user", "content": prompt})
        with st.chat_message("user"):
            st.write(prompt)

        with st.chat_message("assistant"):
            with st.spinner("Thinking..."):
                resp = requests.post(
                    f"{API_URL}/chat",
                    json={"session_id": st.session_state.session_id, "question": prompt},
                )
            if resp.status_code == 200:
                answer = resp.json()["answer"]
                st.write(answer)
                st.session_state.messages.append({"role": "assistant", "content": answer})
            else:
                error_msg = f"Error: {resp.text}"
                st.error(error_msg)
                st.session_state.messages.append({"role": "assistant", "content": error_msg})
