from fastapi import APIRouter, HTTPException

from providers.exceptions import (
    ProviderAuthenticationError,
    ProviderConfigurationError,
    ProviderDownstreamError,
    ProviderRateLimitError,
    ProviderUnavailableError,
)
from schemas.chat_schema import ChatRequest, ChatResponse
from services.ai_service import AIService

router = APIRouter(prefix="/ai", tags=["AI"])

service = AIService()


@router.post("/chat", response_model=ChatResponse)
def chat(request: ChatRequest):
    try:
        answer = service.ask_ai(
            request.provider,
            request.messages,
            request.system_prompt
        )
    except ProviderUnavailableError as error:
        raise HTTPException(
            status_code=503,
            detail="AI provider is temporarily unavailable."
        ) from error
    except ProviderRateLimitError as error:
        raise HTTPException(
            status_code=429,
            detail="AI provider rate limit reached."
        ) from error
    except (ProviderAuthenticationError, ProviderConfigurationError) as error:
        raise HTTPException(
            status_code=500,
            detail="AI provider configuration failed."
        ) from error
    except ProviderDownstreamError as error:
        raise HTTPException(
            status_code=502,
            detail="AI provider returned an unexpected error."
        ) from error

    return ChatResponse(response=answer)
