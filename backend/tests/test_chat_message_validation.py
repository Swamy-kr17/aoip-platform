import unittest

from fastapi import FastAPI
from fastapi.testclient import TestClient
from pydantic import ValidationError

from api.chat import router as chat_router
from schemas.chat_schema import ChatRequest, Message


class ChatMessageValidationTests(unittest.TestCase):
    def test_empty_messages_are_rejected_by_schema(self):
        with self.assertRaises(ValidationError):
            ChatRequest(messages=[])

    def test_empty_messages_return_422_from_chat_endpoint(self):
        app = FastAPI()
        app.include_router(chat_router)
        client = TestClient(app)

        response = client.post(
            "/ai/chat",
            json={
                "provider": "auto",
                "messages": [],
            },
        )

        self.assertEqual(response.status_code, 422)

    def test_one_valid_message_is_accepted(self):
        messages = [Message(role="user", content="Hello")]

        request = ChatRequest(messages=messages)

        self.assertEqual(request.messages, messages)


if __name__ == "__main__":
    unittest.main()
