from dotenv import load_dotenv
import os


def get_api_key():
    # Load the .env file
    load_dotenv()

    # Fetch the API key
    api_key = os.getenv("OPENAI_API_KEY")

    # Ensure the key is not None
    if not api_key:
        raise ValueError(
            "OPENAI_API_KEY not found. Make sure it's set in the .env file."
        )

    return api_key
