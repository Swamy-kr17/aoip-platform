import unittest

from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError

from api.chat import router as chat_router
from schemas.chat_schema import ChatRequest, Message


class ChatProviderValidationTests(unittest.TestCase):
    def test_supported_providers_are_accepted(self):
        messages = [Message(role="user", content="Hello")]

        for provider_name in ("auto", "gemini", "openai", "ollama"):
            with self.subTest(provider_name=provider_name):
                request = ChatRequest(provider=provider_name, messages=messages)
                self.assertEqual(request.provider, provider_name)

    def test_claude_is_rejected_by_schema(self):
        with self.assertRaises(ValidationError):
            ChatRequest(
                provider="claude",
                messages=[Message(role="user", content="Hello")],
            )

    def test_invalid_provider_returns_422_from_chat_endpoint(self):
        app = FastAPI()
        app.include_router(chat_router)
        client = TestClient(app)

        response = client.post(
            "/ai/chat",
            json={
                "provider": "claude",
                "messages": [{"role": "user", "content": "Hello"}],
            },
        )

        self.assertEqual(response.status_code, 422)


if __name__ == "__main__":
    unittest.main()
