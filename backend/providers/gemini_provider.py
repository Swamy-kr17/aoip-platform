from google import genai
from google.genai import types, errors

from config import GEMINI_API_KEY


class GeminiProvider:
    def __init__(self):
        self.client = genai.Client(api_key=GEMINI_API_KEY)
        self.model = "gemini-3.5-flash"

    def generate_response(self, messages, system_prompt):
        try:
            # Convert AOIP messages into one prompt
            prompt = ""

            for message in messages:
                prompt += f"{message.role.capitalize()}: {message.content}\n"
                prompt += "Assistant:"

            # Build config
            if system_prompt:
                config = types.GenerateContentConfig(
                    system_instruction=system_prompt
                )
            else:
                config = None

            # Generate response
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=config
            )

            return response.text

        except errors.ServerError as e:
            print("Gemini Server Error:", e)
            return f"Gemini Server Error: {e}"

        except Exception as e:
            print("General Error:", repr(e))
            return f"Error: {e}"