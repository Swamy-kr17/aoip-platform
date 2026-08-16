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

from config import OPENROUTER_API_KEY
from providers.exceptions import (
    ProviderAuthenticationError,
    ProviderConfigurationError,
    ProviderDownstreamError,
    ProviderRateLimitError,
    ProviderUnavailableError,
)


class OpenRouterProvider:
    def __init__(self):
        if not OPENROUTER_API_KEY:
            raise ProviderConfigurationError(
                "OpenRouter provider is not configured."
            )

        try:
            self.client = OpenAI(
                api_key=OPENROUTER_API_KEY,
                base_url="https://openrouter.ai/api/v1",
            )
        except Exception as error:
            raise ProviderConfigurationError(
                "OpenRouter provider is not configured."
            ) from error

        self.model = "openrouter/free"

    def generate_response(self, messages, system_prompt=None):
        conversation = []

        if system_prompt:
            conversation.append({"role": "system", "content": system_prompt})

        for message in messages:
            conversation.append(
                {"role": message.role, "content": message.content}
            )

        try:
            response = self.client.chat.completions.create(
                model=self.model,
                messages=conversation,
            )
            content = response.choices[0].message.content

            if content is None:
                raise ProviderDownstreamError(
                    "OpenRouter provider returned an empty response."
                )

            return content

        except ProviderDownstreamError:
            raise

        except RateLimitError as error:
            raise ProviderRateLimitError(
                "OpenRouter provider rate limit was reached."
            ) from error

        except (AuthenticationError, PermissionDeniedError) as error:
            raise ProviderAuthenticationError(
                "OpenRouter provider authentication failed."
            ) from error

        except (APIConnectionError, APITimeoutError, InternalServerError) as error:
            raise ProviderUnavailableError(
                "OpenRouter provider is temporarily unavailable."
            ) from error

        except APIStatusError as error:
            if error.status_code in (401, 403):
                raise ProviderAuthenticationError(
                    "OpenRouter provider authentication failed."
                ) from error

            if error.status_code == 429:
                raise ProviderRateLimitError(
                    "OpenRouter provider rate limit was reached."
                ) from error

            if 500 <= error.status_code < 600:
                raise ProviderUnavailableError(
                    "OpenRouter provider is temporarily unavailable."
                ) from error

            raise ProviderDownstreamError(
                "OpenRouter provider returned an unexpected error."
            ) from error

        except Exception as error:
            raise ProviderDownstreamError(
                "OpenRouter provider returned an unexpected error."
            ) from error
