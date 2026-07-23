from services.provider_factory import ProviderFactory

class AIService:

    def ask_ai(self, provider_name: str, messages):

        provider = ProviderFactory.get_provider(provider_name)

        return provider.generate_response(messages)