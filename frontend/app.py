import uuid

import requests
import streamlit as st

API_URL = "http://localhost:8000"

st.set_page_config(page_title="Student Tutoring Agent", layout="wide")

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
            st.success(f"Syllabus uploaded: {result.get('course_name', 'Unknown Course')}")
        else:
            st.error(f"Error: {resp.text}")

    st.subheader("2. Textbook")
    textbook_file = st.file_uploader("Upload your textbook (PDF)", type=["pdf"], key="textbook")
    if textbook_file and not st.session_state.textbook_uploaded:
        with st.spinner("Processing textbook (this may take a minute)..."):
            resp = requests.post(
                f"{API_URL}/upload-textbook",
                files={"file": (textbook_file.name, textbook_file.getvalue(), "application/pdf")},
                data={"session_id": st.session_state.session_id},
            )
        if resp.status_code == 200:
            result = resp.json()
            st.session_state.textbook_uploaded = True
            st.success(f"Textbook uploaded: {result.get('chunks_stored', 0)} chunks indexed")
        else:
            st.error(f"Error: {resp.text}")

    if st.session_state.topics:
        st.subheader("Topics in your syllabus")
        for topic in st.session_state.topics:
            st.write(f"- {topic}")

st.title("Student Tutoring Agent")

if not st.session_state.syllabus_uploaded or not st.session_state.textbook_uploaded:
    st.info("Please upload both your syllabus and textbook in the sidebar to start chatting.")

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
