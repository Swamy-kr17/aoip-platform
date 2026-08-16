import unittest
from unittest.mock import Mock, patch

from pydantic import ValidationError

from providers.exceptions import (
    ProviderAuthenticationError,
    ProviderConfigurationError,
    ProviderDownstreamError,
    ProviderRateLimitError,
    ProviderUnavailableError,
)
from providers.openrouter_provider import OpenRouterProvider
from schemas.chat_schema import ChatRequest, Message
from services.provider_factory import ProviderFactory


class FakeAuthenticationError(Exception):
    pass


class FakeRateLimitError(Exception):
    pass


class FakeConnectionError(Exception):
    pass


class OpenRouterProviderTests(unittest.TestCase):
    def create_provider(self):
        provider = OpenRouterProvider.__new__(OpenRouterProvider)
        provider.client = Mock()
        provider.model = "openrouter/free"
        return provider

    def test_successful_response_preserves_full_conversation_and_system_prompt(self):
        provider = self.create_provider()
        completion = Mock()
        completion.choices = [Mock(message=Mock(content="OpenRouter response"))]
        provider.client.chat.completions.create.return_value = completion
        messages = [
            Message(role="user", content="First question"),
            Message(role="assistant", content="First answer"),
            Message(role="user", content="Follow-up question"),
        ]

        response = provider.generate_response(messages, "You are concise.")

        self.assertEqual(response, "OpenRouter response")
        provider.client.chat.completions.create.assert_called_once_with(
            model="openrouter/free",
            messages=[
                {"role": "system", "content": "You are concise."},
                {"role": "user", "content": "First question"},
                {"role": "assistant", "content": "First answer"},
                {"role": "user", "content": "Follow-up question"},
            ],
        )

    def test_authentication_error_maps_to_provider_authentication_error(self):
        provider = self.create_provider()
        provider.client.chat.completions.create.side_effect = FakeAuthenticationError()

        with patch(
            "providers.openrouter_provider.AuthenticationError",
            FakeAuthenticationError,
        ):
            with self.assertRaises(ProviderAuthenticationError):
                provider.generate_response([Message(role="user", content="Hello")])

    def test_rate_limit_error_maps_to_provider_rate_limit_error(self):
        provider = self.create_provider()
        provider.client.chat.completions.create.side_effect = FakeRateLimitError()

        with patch(
            "providers.openrouter_provider.RateLimitError",
            FakeRateLimitError,
        ):
            with self.assertRaises(ProviderRateLimitError):
                provider.generate_response([Message(role="user", content="Hello")])

    def test_connection_error_maps_to_provider_unavailable_error(self):
        provider = self.create_provider()
        provider.client.chat.completions.create.side_effect = FakeConnectionError()

        with patch(
            "providers.openrouter_provider.APIConnectionError",
            FakeConnectionError,
        ):
            with self.assertRaises(ProviderUnavailableError):
                provider.generate_response([Message(role="user", content="Hello")])

    def test_unexpected_error_maps_to_provider_downstream_error(self):
        provider = self.create_provider()
        provider.client.chat.completions.create.side_effect = RuntimeError(
            "raw upstream failure"
        )

        with self.assertRaises(ProviderDownstreamError):
            provider.generate_response([Message(role="user", content="Hello")])

    def test_missing_key_maps_to_provider_configuration_error(self):
        with patch("providers.openrouter_provider.OPENROUTER_API_KEY", None):
            with self.assertRaises(ProviderConfigurationError):
                OpenRouterProvider()

    def test_provider_factory_returns_openrouter_provider(self):
        with patch("providers.openrouter_provider.OPENROUTER_API_KEY", "test-key"):
            with patch("providers.openrouter_provider.OpenAI") as openai_client:
                provider = ProviderFactory.get_provider("openrouter")

        self.assertIsInstance(provider, OpenRouterProvider)
        openai_client.assert_called_once_with(
            api_key="test-key",
            base_url="https://openrouter.ai/api/v1",
        )

    def test_chat_request_accepts_openrouter(self):
        request = ChatRequest(
            provider="openrouter",
            messages=[Message(role="user", content="Hello")],
        )

        self.assertEqual(request.provider, "openrouter")

    def test_other_invalid_provider_remains_rejected(self):
        with self.assertRaises(ValidationError):
            ChatRequest(
                provider="claude",
                messages=[Message(role="user", content="Hello")],
            )


if __name__ == "__main__":
    unittest.main()
