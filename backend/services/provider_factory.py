from providers.gemini_provider import GeminiProvider
from providers.openai_provider import OpenAIProvider
from providers.ollama_provider import OllamaProvider
from providers.openrouter_provider import OpenRouterProvider


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

        elif provider_name == "openrouter":
            return OpenRouterProvider()

        else:
            raise ValueError(f"Unknown provider: {provider_name}")
