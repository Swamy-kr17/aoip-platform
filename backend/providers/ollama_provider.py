import requests

from providers.exceptions import (
    ProviderAuthenticationError,
    ProviderDownstreamError,
    ProviderRateLimitError,
    ProviderUnavailableError,
)


class OllamaProvider:

    def generate_response(self, messages, system_prompt=None):
        prompt = ""
        if system_prompt:
            prompt += f"System: {system_prompt}\n\n"

        for message in messages:
            prompt += f"{message.role.capitalize()}: {message.content}\n"
        prompt += "Assistant:"
        url = "http://localhost:11434/api/generate"

        payload = {
            "model": "llama3.2:3b",
            "prompt": prompt,
            "stream": False
        }

        try:
            response = requests.post(
                url,
                json=payload,
                timeout=120
            )
        except (requests.exceptions.ConnectionError, requests.exceptions.Timeout) as error:
            raise ProviderUnavailableError(
                "Ollama provider is temporarily unavailable."
            ) from error

        if response.status_code == 200:
            try:
                return response.json()["response"]
            except (ValueError, KeyError, TypeError) as error:
                raise ProviderDownstreamError(
                    "Ollama provider returned an unexpected response."
                ) from error

        if response.status_code in (401, 403):
            raise ProviderAuthenticationError(
                "Ollama provider authentication failed."
            )

        if response.status_code == 429:
            raise ProviderRateLimitError("Ollama provider rate limit was reached.")

        if 500 <= response.status_code < 600:
            raise ProviderUnavailableError("Ollama provider is temporarily unavailable.")

        raise ProviderDownstreamError(
            "Ollama provider returned an unexpected error."
        )
