from services.provider_factory import ProviderFactory

class AIService:

    def ask_ai(self, provider_name, messages, system_prompt):

        provider = ProviderFactory.get_provider(provider_name)

        return provider.generate_response(messages, system_prompt)