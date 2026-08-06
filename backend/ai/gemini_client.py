import os
import json
from dotenv import load_dotenv
from google import genai

load_dotenv()


class GeminiClient:
    """
    Handles all communication with Gemini.
    """

    def __init__(self):

        self.client = genai.Client(
            api_key=os.getenv("GEMINI_API_KEY")
        )

        self.model = "gemini-flash-latest"
    def generate_response(self, prompt):
        """
        Sends a prompt to Gemini.
        """

        try:

            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )

            text = response.text.strip()

            try:
                return json.loads(text)

            except json.JSONDecodeError:
                return text

        except Exception as e:

            return f"Gemini Error: {e}"