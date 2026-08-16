from google import genai
from google.genai import types, errors

from config import GEMINI_API_KEY
from providers.exceptions import (
    ProviderAuthenticationError,
    ProviderConfigurationError,
    ProviderDownstreamError,
    ProviderRateLimitError,
    ProviderUnavailableError,
)


class GeminiProvider:
    def __init__(self):
        if not GEMINI_API_KEY:
            raise ProviderConfigurationError("Gemini provider is not configured.")

        try:
            self.client = genai.Client(api_key=GEMINI_API_KEY)
        except Exception as error:
            raise ProviderConfigurationError(
                "Gemini provider is not configured."
            ) from error

        self.model = "gemini-3.5-flash"

    def generate_response(self, messages, system_prompt):
        try:
            # Convert AOIP messages into one prompt
            prompt = ""

            for message in messages:
                prompt += f"{message.role.capitalize()}: {message.content}\n"
                prompt += "Assistant:"

            # Build config
            if system_prompt:
                config = types.GenerateContentConfig(
                    system_instruction=system_prompt
                )
            else:
                config = None

            # Generate response
            response = self.client.models.generate_content(
                model=self.model,
                contents=prompt,
                config=config
            )

            return response.text

        except errors.ServerError as error:
            raise ProviderUnavailableError(
                "Gemini provider is temporarily unavailable."
            ) from error

        except errors.ClientError as error:
            if error.code == 429:
                raise ProviderRateLimitError(
                    "Gemini provider rate limit was reached."
                ) from error

            if error.code in (401, 403):
                raise ProviderAuthenticationError(
                    "Gemini provider authentication failed."
                ) from error

            raise ProviderDownstreamError(
                "Gemini provider returned an unexpected error."
            ) from error

        except errors.APIError as error:
            raise ProviderDownstreamError(
                "Gemini provider returned an unexpected error."
            ) from error

        except Exception as error:
            raise ProviderDownstreamError(
                "Gemini provider returned an unexpected error."
            ) from error
