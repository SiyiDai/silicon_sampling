from openai import OpenAI
from get_api_key import get_api_key

api_key = get_api_key()
client = OpenAI(api_key=api_key)


def generate_response(prompt):
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # or "gpt-4o", just more expensive
        store=True,
        messages=[
            {"role": "system", "content": "You are a helpful assistant."},
            {"role": "user", "content": prompt},
        ],
        max_tokens=100,
    )
    return response.choices[0].message
