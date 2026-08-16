from typing import List, Literal, Optional
from pydantic import BaseModel, Field


class Message(BaseModel):
    role: str
    content: str


class ChatRequest(BaseModel):
    provider: Literal["auto", "gemini", "openai", "ollama", "openrouter"] = "gemini"
    system_prompt: Optional[str] = None
    messages: List[Message] = Field(min_length=1)


class ChatResponse(BaseModel):
    response: str
