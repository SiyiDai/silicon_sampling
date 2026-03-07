import json
from openai import OpenAI

from get_api_key import get_api_key

api_key = get_api_key()
client = OpenAI(api_key=api_key)


def generate_star_rating(context):
    """
    Predict the star rating (1-5) based on survey responses.

    Args:
        context (str): All survey question/answer pairs except Q48.

    Returns:
        dict: Parsed output with star_rating and raw text.
    """
    response = client.chat.completions.create(
        model="gpt-5.1",
        messages=[
            {
                "role": "system",
                "content": (
                    "You are predicting a survey respondent's hotel star rating (1-5). "
                    "Use all provided answers as evidence."
                ),
            },
            {
                "role": "user",
                "content": (
                    f"Survey responses (excluding the star rating question):\n{context}\n\n"
                    "Return JSON with keys:\n"
                    "- star_rating (integer 1-5)\n"
                    "Only return valid JSON."
                ),
            },
        ],
        max_completion_tokens=120,
        temperature=0.3,
    )

    content = response.choices[0].message.content or ""
    try:
        parsed = json.loads(content)
    except json.JSONDecodeError:
        parsed = {"star_rating": None}

    return {
        "star_rating": parsed.get("star_rating"),
        "raw": content,
    }
