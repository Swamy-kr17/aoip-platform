from services.provider_factory import ProviderFactory
from services.task_analyzer import TaskAnalyzer


class AIService:

    def ask_ai(self, provider_name, messages, system_prompt):
        analyzer = TaskAnalyzer()

        task = analyzer.analyze(messages)
        print(f"Detected task: {task}")

        provider = ProviderFactory.get_provider(provider_name)

        return provider.generate_response(messages, system_prompt)