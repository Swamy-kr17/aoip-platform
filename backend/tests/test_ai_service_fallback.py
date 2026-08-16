import unittest
from unittest.mock import Mock, call, patch

from providers.exceptions import (
    ProviderAuthenticationError,
    ProviderConfigurationError,
    ProviderRateLimitError,
    ProviderUnavailableError,
)
from schemas.chat_schema import Message
from services.ai_service import AIService


class AIServiceFallbackTests(unittest.TestCase):
    def create_provider(self, response=None, error=None):
        provider = Mock()
        if error:
            provider.generate_response.side_effect = error
        else:
            provider.generate_response.return_value = response
        return provider

    def ask_ai(self, provider_name, content, providers):
        messages = [Message(role="user", content=content)]

        with patch(
            "services.ai_service.ProviderFactory.get_provider",
            side_effect=lambda name: providers[name],
        ) as get_provider:
            result = AIService().ask_ai(provider_name, messages, None)

        return result, get_provider, messages

    def test_auto_coding_returns_openai_response_without_fallback(self):
        openai = self.create_provider(response="OpenAI response")
        openrouter = self.create_provider(response="OpenRouter response")

        result, get_provider, _ = self.ask_ai(
            "auto",
            "Write a Python function",
            {"openai": openai, "openrouter": openrouter},
        )

        self.assertEqual(result, "OpenAI response")
        self.assertEqual(get_provider.call_args_list, [call("openai")])
        openrouter.generate_response.assert_not_called()

    def test_auto_coding_rate_limit_falls_back_to_openrouter(self):
        openai = self.create_provider(error=ProviderRateLimitError("rate limited"))
        openrouter = self.create_provider(response="OpenRouter response")

        result, get_provider, _ = self.ask_ai(
            "auto",
            "Write a Python function",
            {"openai": openai, "openrouter": openrouter},
        )

        self.assertEqual(result, "OpenRouter response")
        self.assertEqual(
            get_provider.call_args_list,
            [call("openai"), call("openrouter")],
        )

    def test_auto_coding_unavailable_falls_back_to_openrouter(self):
        openai = self.create_provider(error=ProviderUnavailableError("unavailable"))
        openrouter = self.create_provider(response="OpenRouter response")

        result, get_provider, _ = self.ask_ai(
            "auto",
            "Write a Python function",
            {"openai": openai, "openrouter": openrouter},
        )

        self.assertEqual(result, "OpenRouter response")
        self.assertEqual(
            get_provider.call_args_list,
            [call("openai"), call("openrouter")],
        )

    def test_auto_translation_rate_limit_falls_back_to_openrouter(self):
        gemini = self.create_provider(error=ProviderRateLimitError("rate limited"))
        openrouter = self.create_provider(response="OpenRouter response")

        result, get_provider, _ = self.ask_ai(
            "auto",
            "Translate this to Kannada",
            {"gemini": gemini, "openrouter": openrouter},
        )

        self.assertEqual(result, "OpenRouter response")
        self.assertEqual(
            get_provider.call_args_list,
            [call("gemini"), call("openrouter")],
        )

    def test_auto_general_returns_openrouter_response_without_fallback(self):
        openrouter = self.create_provider(response="OpenRouter response")
        ollama = self.create_provider(response="Ollama response")

        result, get_provider, _ = self.ask_ai(
            "auto",
            "Tell me a fun fact",
            {"openrouter": openrouter, "ollama": ollama},
        )

        self.assertEqual(result, "OpenRouter response")
        self.assertEqual(get_provider.call_args_list, [call("openrouter")])
        ollama.generate_response.assert_not_called()

    def test_auto_general_unavailable_falls_back_to_ollama(self):
        openrouter = self.create_provider(error=ProviderUnavailableError("unavailable"))
        ollama = self.create_provider(response="Ollama response")

        result, get_provider, _ = self.ask_ai(
            "auto",
            "Tell me a fun fact",
            {"openrouter": openrouter, "ollama": ollama},
        )

        self.assertEqual(result, "Ollama response")
        self.assertEqual(
            get_provider.call_args_list,
            [call("openrouter"), call("ollama")],
        )

    def test_auto_all_fallback_providers_fail_with_final_error(self):
        openrouter = self.create_provider(error=ProviderUnavailableError("first failure"))
        ollama = self.create_provider(error=ProviderUnavailableError("second failure"))
        gemini = self.create_provider(error=ProviderUnavailableError("final failure"))
        messages = [Message(role="user", content="Tell me a fun fact")]

        with patch(
            "services.ai_service.ProviderFactory.get_provider",
            side_effect=lambda name: {
                "openrouter": openrouter,
                "ollama": ollama,
                "gemini": gemini,
            }[name],
        ) as get_provider:
            with self.assertRaises(ProviderUnavailableError):
                AIService().ask_ai("auto", messages, None)

        self.assertEqual(
            get_provider.call_args_list,
            [call("openrouter"), call("ollama"), call("gemini")],
        )

    def test_auto_authentication_error_does_not_fallback(self):
        openai = self.create_provider(
            error=ProviderAuthenticationError("authentication failed")
        )
        messages = [Message(role="user", content="Write a Python function")]

        with patch(
            "services.ai_service.ProviderFactory.get_provider",
            return_value=openai,
        ) as get_provider:
            with self.assertRaises(ProviderAuthenticationError):
                AIService().ask_ai("auto", messages, None)

        self.assertEqual(get_provider.call_args_list, [call("openai")])

    def test_auto_configuration_error_does_not_fallback(self):
        openai = self.create_provider(
            error=ProviderConfigurationError("configuration failed")
        )
        messages = [Message(role="user", content="Write a Python function")]

        with patch(
            "services.ai_service.ProviderFactory.get_provider",
            return_value=openai,
        ) as get_provider:
            with self.assertRaises(ProviderConfigurationError):
                AIService().ask_ai("auto", messages, None)

        self.assertEqual(get_provider.call_args_list, [call("openai")])

    def test_manual_openai_error_does_not_fallback(self):
        openai = self.create_provider(error=ProviderRateLimitError("rate limited"))
        messages = [Message(role="user", content="Tell me a fun fact")]

        with patch(
            "services.ai_service.ProviderFactory.get_provider",
            return_value=openai,
        ) as get_provider:
            with self.assertRaises(ProviderRateLimitError):
                AIService().ask_ai("openai", messages, None)

        self.assertEqual(get_provider.call_args_list, [call("openai")])

    def test_manual_openrouter_error_does_not_fallback(self):
        openrouter = self.create_provider(
            error=ProviderUnavailableError("unavailable")
        )
        messages = [Message(role="user", content="Tell me a fun fact")]

        with patch(
            "services.ai_service.ProviderFactory.get_provider",
            return_value=openrouter,
        ) as get_provider:
            with self.assertRaises(ProviderUnavailableError):
                AIService().ask_ai("openrouter", messages, None)

        self.assertEqual(get_provider.call_args_list, [call("openrouter")])

    def test_auto_never_calls_a_provider_twice(self):
        openai = self.create_provider(error=ProviderRateLimitError("rate limited"))
        openrouter = self.create_provider(error=ProviderUnavailableError("unavailable"))
        ollama = self.create_provider(response="Ollama response")

        result, get_provider, _ = self.ask_ai(
            "auto",
            "Write a Python function",
            {"openai": openai, "openrouter": openrouter, "ollama": ollama},
        )

        self.assertEqual(result, "Ollama response")
        self.assertEqual(
            get_provider.call_args_list,
            [call("openai"), call("openrouter"), call("ollama")],
        )
        openai.generate_response.assert_called_once()
        openrouter.generate_response.assert_called_once()
        ollama.generate_response.assert_called_once()


if __name__ == "__main__":
    unittest.main()
