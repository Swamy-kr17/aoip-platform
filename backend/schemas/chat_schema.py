from typing import List, Optional
from pydantic import BaseModel


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    provider: str = "gemini"
    system_prompt: Optional[str] = None
    messages: List[Message]


class ChatResponse(BaseModel):
    response: str