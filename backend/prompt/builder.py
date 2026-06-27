SYSTEM_PROMPT_TEMPLATE = """You are a tutor for the course "{course_name}".

STRICT RULES — you must follow ALL of these with no exceptions:
1. You may ONLY answer questions about these topics: {topics}
2. Prefer information from the CONTEXT below when answering.
3. If the CONTEXT contains enough information, use it and reference which chunk you drew from.
4. If the question is about a listed topic but the CONTEXT does not contain enough information,
   answer using your general knowledge but start your response with:
   "**Note: I couldn't find this in your textbook, so the following is based on general knowledge.**"
5. Be helpful, clear, and educational in your explanations — break down complex ideas for a student.

CONTEXT FROM TEXTBOOK (chunks numbered for reference):
{context}
"""

GENERAL_KNOWLEDGE_PROMPT_TEMPLATE = """You are a helpful tutor. The student is enrolled in "{course_name}" but has asked a question that is not covered in their course material.

Answer the question clearly and educationally using your general knowledge. Be concise and helpful."""


def build_prompt(
    topics: list[str],
    retrieved_chunks: list[str],
    question: str,
    course_name: str = "",
) -> list[dict]:
    topics_str = ", ".join(topics)

    numbered_chunks = []
    for i, chunk in enumerate(retrieved_chunks, 1):
        numbered_chunks.append(f"[Chunk {i}]\n{chunk}")
    context_str = "\n\n---\n\n".join(numbered_chunks)

    system_message = SYSTEM_PROMPT_TEMPLATE.format(
        course_name=course_name or "this course",
        topics=topics_str,
        context=context_str,
    )

    return [
        {"role": "system", "content": system_message},
        {"role": "user", "content": question},
    ]


def build_general_knowledge_prompt(question: str, course_name: str = "") -> list[dict]:
    system_message = GENERAL_KNOWLEDGE_PROMPT_TEMPLATE.format(
        course_name=course_name or "this course",
    )

    return [
        {"role": "system", "content": system_message},
        {"role": "user", "content": question},
    ]
