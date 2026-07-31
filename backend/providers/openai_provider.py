from openai import OpenAI
from openai import RateLimitError
from config import OPENAI_API_KEY


class OpenAIProvider:

    def __init__(self):
        self.client = OpenAI(api_key=OPENAI_API_KEY)

    def generate_response(self, messages, system_prompt=None):
        prompt = messages[-1].content
        try:
            response = self.client.responses.create(
                model="gpt-5.5",
                input=prompt
            )
            return response.output_text

        except RateLimitError:
            return (
                "OpenAI API quota exceeded. "
                "Please check your OpenAI Platform billing or available credits."
            )

        except Exception as e:
            return f"OpenAI Error: {e}"