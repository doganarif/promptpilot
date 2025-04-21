import os
import requests
import json
from .base import BaseProvider

class LlamaProvider(BaseProvider):
    def __init__(self, api_key=None, model=None, api_url=None):
        self.api_key = api_key or os.getenv('LLAMA_API_KEY')
        if not self.api_key:
            raise ValueError("LLAMA_API_KEY not found in environment variables")

        self.model = model or os.getenv('PROMPTCTL_LLAMA_MODEL', 'llama-3-70b-instruct')
        self.api_url = api_url or os.getenv('LLAMA_API_URL', 'https://api.llama-api.com')

    def send_prompt(self, prompt: str):
        headers = {
            "Content-Type": "application/json",
            "Authorization": f"Bearer {self.api_key}"
        }

        payload = {
            "model": self.model,
            "messages": [{"role": "user", "content": prompt}],
            "max_tokens": 1000,
            "temperature": 0.7
        }

        response = requests.post(
            f"{self.api_url}/chat/completions",
            headers=headers,
            data=json.dumps(payload)
        )

        if response.status_code != 200:
            raise Exception(f"Error calling Llama API: {response.text}")

        result = response.json()
        response_text = result["choices"][0]["message"]["content"]

        # Some Llama APIs may not include token counts - handle both cases
        if "usage" in result:
            tokens_used = result["usage"]["total_tokens"]
        else:
            # Estimate token count based on text length (rough approximation)
            tokens_used = len(response_text.split())

        return response_text, tokens_used
