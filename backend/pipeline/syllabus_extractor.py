import json

from openai import OpenAI

client = OpenAI()

EXTRACTION_PROMPT = """Extract the following information from this syllabus text and return ONLY valid JSON with no markdown formatting, no explanation, no extra text.

The JSON must have exactly these keys:
{
  "course_name": "",
  "professor": "",
  "topics_covered": [],
  "weekly_schedule": {},
  "textbook": ""
}

- "topics_covered" should be a list of all topics/subjects mentioned in the syllabus
- "weekly_schedule" should map week numbers or dates to topics (e.g. {"Week 1": "Introduction", "Week 2": "Chapter 2"})
- If a field is not found, use an empty string or empty list/object

Syllabus text:
"""


def extract_syllabus(raw_text: str) -> dict:
    response = client.chat.completions.create(
        model="gpt-4o",
        messages=[
            {"role": "system", "content": "You extract structured data from syllabi. Return only valid JSON."},
            {"role": "user", "content": EXTRACTION_PROMPT + raw_text},
        ],
        temperature=0,
    )

    content = response.choices[0].message.content.strip()
    if content.startswith("```"):
        content = content.split("\n", 1)[1]
        content = content.rsplit("```", 1)[0]

    try:
        data = json.loads(content)
    except json.JSONDecodeError:
        data = {
            "course_name": "",
            "professor": "",
            "topics_covered": [],
            "weekly_schedule": {},
            "textbook": "",
        }

    for key, default in [
        ("course_name", ""),
        ("professor", ""),
        ("topics_covered", []),
        ("weekly_schedule", {}),
        ("textbook", ""),
    ]:
        data.setdefault(key, default)

    return data
