from services.provider_factory import ProviderFactory
from services.task_analyzer import TaskAnalyzer


class AIService:

    def ask_ai(self, provider_name, messages, system_prompt):
        analyzer = TaskAnalyzer()

        task = analyzer.analyze(messages)
        recommended_provider = analyzer.recommend_provider(task)

        print(f"Detected task: {task}")
        print(f"Recommended provider: {recommended_provider}")

        # Use the provider requested by the user (for now)
        provider = ProviderFactory.get_provider(provider_name)

        return provider.generate_response(messages, system_prompt)