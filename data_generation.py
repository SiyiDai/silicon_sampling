from openai import OpenAI
from get_api_key import get_api_key

api_key = get_api_key()
client = OpenAI(api_key=api_key)


def generate_response(context):
    """
    Generate a response based on the persona context.

    Args:
        context (str): A conditioning context describing the persona.

    Returns:
        str: The AI-generated response.
    """
    response = client.chat.completions.create(
        model="gpt-4o-mini",  # Use "gpt-4" or "gpt-4-turbo" based on your requirements
        messages=[
            {
                "role": "system",
                "content": "You will be provided with a descriptive context and please imagine you are this person and provide precise answers based on the provided background",
            },
            {
                "role": "user",
                "content": (
                    f"{context}\n\n"
                    "Please answer the following questions without given reasons:\n"
                    "1. Do you prefer online shopping or offline shopping for lamps?\n"
                    "2. What is the maximum amount you are willing to pay for a lamp (in euros)?\n"
                    "3. How many lamps would you buy per year?\n"
                    "4. Among the following aspects: Brightness, Efficiency, Affordability, Durability, Design, "
                    "Portability, Convenience, Sustainability, Technology, Safety, which three aspects are the most valued by you?\n"
                    "please answer these questions in a string, for example: online, 100, 1, Efficiency; Affordability; Safety\n"
                ),
            },
        ],
        max_tokens=200,  # Increase max_tokens to allow detailed responses
        temperature=0.7,  # Adjust temperature for creativity (0.7 is a balanced choice)
    )

    # Extract response content
    content = response.choices[0].message.content
    return content
