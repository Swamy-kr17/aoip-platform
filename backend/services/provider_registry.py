# ProviderRegistry -- capability-aware provider routing
#
# Each task maps to an explicit, ordered list of providers.
# The first entry is the primary (best-fit) provider.
# Subsequent entries are fallbacks tried in order.
#
# To add a new provider: add it to the relevant task lists below.
# To add a new task type: add a new key with its ordered provider list.
# No changes to AIService, TaskAnalyzer, or ProviderFactory are needed.


TASK_PROVIDER_ORDER = {
    "coding":        ["openai",     "openrouter", "ollama"],
    "translation":   ["gemini",     "openrouter", "ollama"],
    "summarization": ["gemini",     "openrouter", "ollama"],
    "writing":       ["openrouter", "ollama",     "gemini"],
    "reasoning":     ["openrouter", "ollama",     "gemini"],
    "general":       ["openrouter", "ollama",     "gemini"],
}


class ProviderRegistry:

    @staticmethod
    def get_providers_for_task(task: str) -> list[str]:
        """
        Return the ordered list of providers for a given task type.

        The first provider in the list is the primary recommendation.
        Remaining providers are fallbacks, tried in order if the primary fails.

        Raises ValueError if the task type is not recognised.
        """
        providers = TASK_PROVIDER_ORDER.get(task)

        if providers is None:
            raise ValueError(
                f"[AOIP] ProviderRegistry: unknown task type '{task}'. "
                f"Supported tasks: {list(TASK_PROVIDER_ORDER.keys())}"
            )

        return list(providers)  # return a copy so callers cannot mutate the registry