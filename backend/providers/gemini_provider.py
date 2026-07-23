from google import genai
from google.genai import errors

from config import GEMINI_API_KEY


class GeminiProvider:
    def __init__(self):
        self.client = genai.Client(api_key=GEMINI_API_KEY)

    def generate_response(self, messages) -> str:
        prompt = messages[-1].content
        try:
            response = self.client.models.generate_content(
                model="gemini-flash-lite-latest",
                contents=prompt,
            )

            return response.text

        except errors.ServerError:
            return "Gemini is currently busy. Please try again in a few moments."

        except Exception as e:
            return f"Error: {e}"