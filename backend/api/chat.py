from fastapi import APIRouter

from schemas.chat_schema import ChatRequest, ChatResponse
from services.ai_service import AIService

router = APIRouter(prefix="/ai", tags=["AI"])

service = AIService()


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):

    answer = service.ask_ai(
        request.provider,
        request.prompt
    )

    return ChatResponse(response=answer)