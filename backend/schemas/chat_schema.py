from pydantic import BaseModel


class ChatRequest(BaseModel):
    provider: str = "gemini"
    prompt: str


class ChatResponse(BaseModel):
    response: str