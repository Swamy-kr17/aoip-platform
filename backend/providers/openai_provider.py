from openai import (
    APIConnectionError,
    APIStatusError,
    APITimeoutError,
    AuthenticationError,
    InternalServerError,
    OpenAI,
    PermissionDeniedError,
    RateLimitError,
)
from config import OPENAI_API_KEY
from providers.exceptions import (
    ProviderAuthenticationError,
    ProviderConfigurationError,
    ProviderDownstreamError,
    ProviderRateLimitError,
    ProviderUnavailableError,
)


class OpenAIProvider:

    def __init__(self):
        if not OPENAI_API_KEY:
            raise ProviderConfigurationError("OpenAI provider is not configured.")

        try:
            self.client = OpenAI(api_key=OPENAI_API_KEY)
        except Exception as error:
            raise ProviderConfigurationError(
                "OpenAI provider is not configured."
            ) from error

    def generate_response(self, messages, system_prompt=None):
        conversation = []

        for message in messages:
            conversation.append({"role": message.role, "content": message.content})

        try:
            response = self.client.responses.create(
                model="gpt-5.5",
                input=conversation,
                instructions=system_prompt or None,
            )
            return response.output_text

        except RateLimitError as error:
            raise ProviderRateLimitError(
                "OpenAI provider rate limit was reached."
            ) from error

        except (AuthenticationError, PermissionDeniedError) as error:
            raise ProviderAuthenticationError(
                "OpenAI provider authentication failed."
            ) from error

        except (APIConnectionError, APITimeoutError, InternalServerError) as error:
            raise ProviderUnavailableError(
                "OpenAI provider is temporarily unavailable."
            ) from error

        except APIStatusError as error:
            if error.status_code in (401, 403):
                raise ProviderAuthenticationError(
                    "OpenAI provider authentication failed."
                ) from error

            if error.status_code == 429:
                raise ProviderRateLimitError(
                    "OpenAI provider rate limit was reached."
                ) from error

            if 500 <= error.status_code < 600:
                raise ProviderUnavailableError(
                    "OpenAI provider is temporarily unavailable."
                ) from error

            raise ProviderDownstreamError(
                "OpenAI provider returned an unexpected error."
            ) from error

        except Exception as error:
            raise ProviderDownstreamError(
                "OpenAI provider returned an unexpected error."
            ) from error
