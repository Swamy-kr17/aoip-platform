import unittest
from unittest.mock import Mock, patch

import requests
from fastapi import FastAPI
from fastapi.testclient import TestClient
from google.genai import errors as gemini_errors

from api.chat import router as chat_router
from providers.exceptions import (
    ProviderAuthenticationError,
    ProviderConfigurationError,
    ProviderDownstreamError,
    ProviderRateLimitError,
    ProviderUnavailableError,
)
from providers.gemini_provider import GeminiProvider
from providers.ollama_provider import OllamaProvider
from providers.openai_provider import OpenAIProvider


class FakeRateLimitError(Exception):
    pass


class ProviderErrorHandlingTests(unittest.TestCase):
    def setUp(self):
        app = FastAPI()
        app.include_router(chat_router)
        self.client = TestClient(app)
        self.request_body = {
            "provider": "auto",
            "messages": [{"role": "user", "content": "Hello"}],
        }

    def post_with_service_error(self, error):
        with patch("api.chat.service.ask_ai", side_effect=error):
            return self.client.post("/ai/chat", json=self.request_body)

    def test_successful_provider_response_returns_200(self):
        with patch("api.chat.service.ask_ai", return_value="Hello from AI"):
            response = self.client.post("/ai/chat", json=self.request_body)

        self.assertEqual(response.status_code, 200)
        self.assertEqual(response.json(), {"response": "Hello from AI"})

    def test_provider_unavailable_returns_503(self):
        response = self.post_with_service_error(ProviderUnavailableError("raw SDK error"))

        self.assertEqual(response.status_code, 503)
        self.assertEqual(response.json()["detail"], "AI provider is temporarily unavailable.")

    def test_provider_rate_limit_returns_429(self):
        response = self.post_with_service_error(ProviderRateLimitError("raw quota error"))

        self.assertEqual(response.status_code, 429)
        self.assertEqual(response.json()["detail"], "AI provider rate limit reached.")

    def test_provider_authentication_returns_500(self):
        response = self.post_with_service_error(
            ProviderAuthenticationError("raw authentication error")
        )

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json()["detail"], "AI provider configuration failed.")

    def test_provider_configuration_returns_500(self):
        response = self.post_with_service_error(
            ProviderConfigurationError("raw configuration error")
        )

        self.assertEqual(response.status_code, 500)
        self.assertEqual(response.json()["detail"], "AI provider configuration failed.")

    def test_provider_downstream_error_returns_502_without_raw_error_text(self):
        response = self.post_with_service_error(
            ProviderDownstreamError("sensitive upstream failure details")
        )

        self.assertEqual(response.status_code, 502)
        self.assertEqual(response.json()["detail"], "AI provider returned an unexpected error.")
        self.assertNotIn("sensitive upstream failure details", response.text)

    def test_gemini_server_error_maps_to_provider_unavailable(self):
        provider = GeminiProvider.__new__(GeminiProvider)
        provider.client = Mock()
        provider.client.models.generate_content.side_effect = gemini_errors.ServerError(
            503,
            {"error": {"message": "raw Gemini failure"}},
        )
        provider.model = "test-model"

        with self.assertRaises(ProviderUnavailableError):
            provider.generate_response([], None)

    def test_openai_rate_limit_maps_to_provider_rate_limit(self):
        provider = OpenAIProvider.__new__(OpenAIProvider)
        provider.client = Mock()
        provider.client.responses.create.side_effect = FakeRateLimitError("raw quota failure")

        with patch("providers.openai_provider.RateLimitError", FakeRateLimitError):
            with self.assertRaises(ProviderRateLimitError):
                provider.generate_response([Mock(content="Hello")], None)

    def test_ollama_connection_failure_maps_to_provider_unavailable(self):
        provider = OllamaProvider()

        with patch(
            "providers.ollama_provider.requests.post",
            side_effect=requests.exceptions.ConnectionError("raw connection failure"),
        ):
            with self.assertRaises(ProviderUnavailableError):
                provider.generate_response([Mock(role="user", content="Hello")], None)


if __name__ == "__main__":
    unittest.main()
