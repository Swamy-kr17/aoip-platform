from providers.gemini_provider import GeminiProvider
from providers.openai_provider import OpenAIProvider
from providers.ollama_provider import OllamaProvider


class ProviderFactory:

    @staticmethod
    def get_provider(provider_name: str):

        provider_name = provider_name.lower()

        if provider_name == "gemini":
            return GeminiProvider()

        elif provider_name == "openai":
            return OpenAIProvider()

        elif provider_name == "ollama":
            return OllamaProvider()

        else:
            raise ValueError(f"Unknown provider: {provider_name}")