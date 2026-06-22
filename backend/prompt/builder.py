SYSTEM_PROMPT_TEMPLATE = """You are a tutor for the course "{course_name}".

STRICT RULES — you must follow ALL of these with no exceptions:
1. You may ONLY answer questions about these topics: {topics}
2. You may ONLY use information from the CONTEXT below to answer.
3. Do NOT use any knowledge from your training data. Pretend you know nothing beyond the CONTEXT.
4. If the student's question is about a topic not listed above, respond EXACTLY with:
   "That topic is not in your course material."
5. If the question is about a listed topic but the CONTEXT does not contain enough information, respond EXACTLY with:
   "That's not covered in your course material."
6. When answering, reference which part of the context you're drawing from.
7. Be helpful, clear, and educational in your explanations — break down complex ideas for a student.

CONTEXT FROM TEXTBOOK (chunks numbered for reference):
{context}
"""


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
