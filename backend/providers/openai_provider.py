class OpenAIProvider:
    """
    Handles communication with OpenAI models.
    """

    def __init__(self):
        self.provider_name = "OpenAI"

    def generate_response(self, prompt: str) -> str:
        """
        Simulates sending a prompt to an AI model.
        """
        return f"[{self.provider_name}] Response to: {prompt}"