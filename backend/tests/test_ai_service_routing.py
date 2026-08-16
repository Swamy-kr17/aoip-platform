import unittest
from unittest.mock import Mock, patch

from schemas.chat_schema import Message
from services.ai_service import AIService


class AIServiceRoutingTests(unittest.TestCase):
    def assert_selected_provider(self, provider_name, message_content, expected_provider):
        fake_provider = Mock()
        fake_provider.generate_response.return_value = "test response"
        messages = [Message(role="user", content=message_content)]

        with patch(
            "services.ai_service.ProviderFactory.get_provider",
            return_value=fake_provider,
        ) as get_provider:
            response = AIService().ask_ai(provider_name, messages, None)

        self.assertEqual(response, "test response")
        get_provider.assert_called_once_with(expected_provider)
        fake_provider.generate_response.assert_called_once_with(messages, None)

    def test_auto_routes_coding_to_openai(self):
        self.assert_selected_provider("auto", "Write a Python function", "openai")

    def test_auto_routes_translation_to_gemini(self):
        self.assert_selected_provider("auto", "Translate this into French", "gemini")

    def test_auto_routes_summarization_to_gemini(self):
        self.assert_selected_provider("auto", "Summarize this document", "gemini")

    def test_auto_routes_general_to_ollama(self):
        self.assert_selected_provider("auto", "Tell me a fun fact", "ollama")

    def test_manual_provider_overrides_recommendation(self):
        for provider_name in ("ollama", "gemini", "openai"):
            with self.subTest(provider_name=provider_name):
                self.assert_selected_provider(
                    provider_name,
                    "Write a Python function",
                    provider_name,
                )


if __name__ == "__main__":
    unittest.main()
