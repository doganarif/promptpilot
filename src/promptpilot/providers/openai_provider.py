"""
OpenAI provider implementation.
"""

import os
from typing import Tuple, Optional

from openai import OpenAI

from .base import BaseProvider


class OpenAIProvider(BaseProvider):
    """
    Provider implementation for OpenAI API.
    """

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Set the OPENAI_API_KEY environment variable.")

        # default to gpt-4 to match docs
        self.model = model or os.getenv('PROMPTCTL_DEFAULT_MODEL', 'gpt-4o')
        self.client = OpenAI(api_key=self.api_key)

    def send_prompt(self, prompt: str) -> Tuple[str, int]:
        resp = self.client.chat.completions.create(
            model=self.model,
            messages=[{"role": "user", "content": prompt}]
        )
        return resp.choices[0].message.content, resp.usage.total_tokens

    @property
    def name(self) -> str:
        return "openai"

    @property
    def supports_streaming(self) -> bool:
        return True
