import requests


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

        response = requests.post(
    url,
    json=payload,
    timeout=120
)

        if response.status_code == 200:
            return response.json()["response"]

        raise Exception(f"Ollama Error: {response.text}")