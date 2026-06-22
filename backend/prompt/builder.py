SYSTEM_PROMPT_TEMPLATE = """You are a tutor for this course ONLY.
You MUST refuse to answer anything not found in the CONTEXT below.
Do not use any knowledge from your training data.
If the answer is not in the CONTEXT, respond with:
"That topic is not covered in your course material."
No exceptions.

SYLLABUS TOPICS: {topics}

CONTEXT FROM TEXTBOOK:
{context}
"""


def build_prompt(topics: list[str], retrieved_chunks: list[str], question: str) -> list[dict]:
    topics_str = ", ".join(topics)
    context_str = "\n\n---\n\n".join(retrieved_chunks)

    system_message = SYSTEM_PROMPT_TEMPLATE.format(
        topics=topics_str,
        context=context_str,
    )

    return [
        {"role": "system", "content": system_message},
        {"role": "user", "content": question},
    ]
