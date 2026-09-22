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
        Sends a prompt to Gemini and returns
        structured JSON when available.
        """

        try:

            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt
            )

            text = response.text.strip()

            # Remove Markdown JSON code fences if Gemini adds them
            if text.startswith("```json"):
                text = text[7:]

            elif text.startswith("```"):
                text = text[3:]

            if text.endswith("```"):
                text = text[:-3]

            text = text.strip()

            # Try to parse JSON
            try:

                return json.loads(text)

            except json.JSONDecodeError:

                # Try to extract JSON object from surrounding text
                start = text.find("{")
                end = text.rfind("}")

                if start != -1 and end != -1:

                    try:
                        return json.loads(
                            text[start:end + 1]
                        )

                    except json.JSONDecodeError:
                        pass

                return text

        except Exception as e:

            return f"Gemini Error: {e}"