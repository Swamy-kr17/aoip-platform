from providers.gemini_provider import GeminiProvider


class AIService:
    """
    Manages AI providers and handles AI requests.
    """

    def __init__(self):
        self.provider = GeminiProvider()

    def ask_ai(self, prompt: str) -> str:
        """
        Sends the prompt to the configured AI provider.
        """
        return self.provider.generate_response(prompt)