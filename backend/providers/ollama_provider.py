import requests


class OllamaProvider:

    def generate_response(self, prompt: str) -> str:
        url = "http://localhost:11434/api/generate"

        payload = {
            "model": "llama3.2:3b",
            "prompt": prompt,
            "stream": False
        }

        response = requests.post(url, json=payload)

        if response.status_code == 200:
            return response.json()["response"]

        raise Exception(f"Ollama Error: {response.text}")