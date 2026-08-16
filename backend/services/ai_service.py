from services.provider_factory import ProviderFactory
from services.task_analyzer import TaskAnalyzer
from providers.exceptions import ProviderRateLimitError, ProviderUnavailableError


class AIService:
    AUTO_FALLBACK_PROVIDERS = {
        "coding": ["openrouter", "ollama"],
        "translation": ["openrouter", "ollama"],
        "summarization": ["openrouter", "ollama"],
        "writing": ["ollama", "gemini"],
        "reasoning": ["ollama", "gemini"],
        "general": ["ollama", "gemini"],
    }

    def ask_ai(self, provider_name, messages, system_prompt):
        analyzer = TaskAnalyzer()

        task = analyzer.analyze(messages)
        recommended_provider = analyzer.recommend_provider(task)

        print(f"Detected task: {task}")
        print(f"Recommended provider: {recommended_provider}")

        if provider_name.lower() != "auto":
            provider = ProviderFactory.get_provider(provider_name)
            return provider.generate_response(messages, system_prompt)

        providers_to_try = [recommended_provider]
        for fallback_provider in self.AUTO_FALLBACK_PROVIDERS[task]:
            if fallback_provider not in providers_to_try:
                providers_to_try.append(fallback_provider)

        for index, selected_provider in enumerate(providers_to_try):
            try:
                provider = ProviderFactory.get_provider(selected_provider)
                return provider.generate_response(messages, system_prompt)
            except (ProviderUnavailableError, ProviderRateLimitError):
                if index == len(providers_to_try) - 1:
                    raise
