from services.provider_factory import ProviderFactory


class AIService:

    def ask_ai(self, provider_name: str, prompt: str) -> str:

        provider = ProviderFactory.get_provider(provider_name)

        return provider.generate_response(prompt)