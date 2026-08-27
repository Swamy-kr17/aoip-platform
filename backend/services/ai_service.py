from services.provider_factory import ProviderFactory
from services.task_analyzer import TaskAnalyzer
from providers.exceptions import ProviderConfigurationError, ProviderDownstreamError, ProviderRateLimitError, ProviderUnavailableError


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

        print(f"[AOIP] Detected task:        {task}")
        print(f"[AOIP] Recommended provider: {recommended_provider}")

        if provider_name.lower() != "auto":
            print(f"[AOIP] Routing mode: manual → using provider: {provider_name.lower()}")
            provider = ProviderFactory.get_provider(provider_name)
            response_text = provider.generate_response(messages, system_prompt)
            return {
                "response":      response_text,
                "task_detected": task,
                "provider_used": provider_name.lower(),
                "routing_mode":  "manual",
            }

        providers_to_try = [recommended_provider]
        for fallback_provider in self.AUTO_FALLBACK_PROVIDERS[task]:
            if fallback_provider not in providers_to_try:
                providers_to_try.append(fallback_provider)

        print(f"[AOIP] Routing mode: auto → will try: {providers_to_try}")

        for index, selected_provider in enumerate(providers_to_try):
            print(f"[AOIP] Trying provider: {selected_provider}")
            try:
                provider = ProviderFactory.get_provider(selected_provider)
                response_text = provider.generate_response(messages, system_prompt)
                print(f"[AOIP] Success → provider used: {selected_provider}")
                return {
                    "response":      response_text,
                    "task_detected": task,
                    "provider_used": selected_provider,
                    "routing_mode":  "auto",
                }
            except (ProviderUnavailableError, ProviderRateLimitError, ProviderConfigurationError, ProviderDownstreamError) as error:
                print(f"[AOIP] Provider '{selected_provider}' failed ({type(error).__name__}) — trying next fallback")
                if index == len(providers_to_try) - 1:
                    print(f"[AOIP] All providers exhausted. Raising final error.")
                    raise

