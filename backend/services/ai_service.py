from services.provider_factory import ProviderFactory
from services.provider_health_tracker import health_tracker
from services.provider_registry import ProviderRegistry
from services.task_analyzer import TaskAnalyzer
from providers.exceptions import ProviderConfigurationError, ProviderDownstreamError, ProviderRateLimitError, ProviderUnavailableError


class AIService:

    def ask_ai(self, provider_name, messages, system_prompt):
        analyzer = TaskAnalyzer()

        task = analyzer.analyze(messages)

        print(f"[AOIP] Detected task: {task}")

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

        providers_to_try = ProviderRegistry.get_providers_for_task(task)

        print(f"[AOIP] Routing mode: auto → registry order for '{task}': {providers_to_try}")

        try:
            available_providers = [p for p in providers_to_try if health_tracker.is_available(p)]
        except Exception as filter_error:
            print(f"[AOIP][Health] Warning: health filter failed ({filter_error}) — using full registry order")
            available_providers = providers_to_try

        if not available_providers:
            print(f"[AOIP][Health] All providers in cooldown — emergency fallback: using full registry order")
            available_providers = providers_to_try
        elif len(available_providers) < len(providers_to_try):
            skipped = [p for p in providers_to_try if not health_tracker.is_available(p)]
            print(f"[AOIP][Health] Skipping unhealthy providers: {skipped}")
            print(f"[AOIP][Health] Eligible providers: {available_providers}")

        for index, selected_provider in enumerate(available_providers):
            print(f"[AOIP] Trying provider: {selected_provider}")
            try:
                provider = ProviderFactory.get_provider(selected_provider)
                response_text = provider.generate_response(messages, system_prompt)
                print(f"[AOIP] Success → provider used: {selected_provider}")
                try:
                    health_tracker.record_success(selected_provider)
                except Exception as tracker_error:
                    print(f"[AOIP][Health] Warning: could not record success for '{selected_provider}': {tracker_error}")
                return {
                    "response":      response_text,
                    "task_detected": task,
                    "provider_used": selected_provider,
                    "routing_mode":  "auto",
                }
            except (ProviderUnavailableError, ProviderRateLimitError, ProviderConfigurationError, ProviderDownstreamError) as error:
                print(f"[AOIP] Provider '{selected_provider}' failed ({type(error).__name__}) — trying next fallback")
                try:
                    health_tracker.record_failure(selected_provider, type(error).__name__)
                except Exception as tracker_error:
                    print(f"[AOIP][Health] Warning: could not record failure for '{selected_provider}': {tracker_error}")
                if index == len(available_providers) - 1:
                    print(f"[AOIP] All providers exhausted. Raising final error.")
                    raise

