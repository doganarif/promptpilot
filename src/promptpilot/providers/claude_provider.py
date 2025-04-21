"""
Claude provider implementation.
"""

import os
from typing import Tuple, Optional
import warnings

import anthropic

from .base import BaseProvider


class ClaudeProvider(BaseProvider):
    """
    Provider implementation for Anthropics's Claude API.
    """

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None):
        self.api_key = api_key or os.getenv('ANTHROPIC_API_KEY')
        if not self.api_key:
            raise ValueError("Anthropic API key not found. Set the ANTHROPIC_API_KEY environment variable.")

        self.model = model or os.getenv('PROMPTCTL_CLAUDE_MODEL', 'claude-3-opus-20240229')
        self.client = anthropic.Client(api_key=self.api_key)

    def send_prompt(self, prompt: str) -> Tuple[str, int]:
        try:
            message = self.client.completions.create(
                model=self.model,
                prompt=prompt,
                max_tokens_to_sample=1000
            )
        except Exception as e:
            raise RuntimeError(f"Claude API error: {e}")

        # Depending on SDK version, use .completion or .completion.text
        response_text = getattr(message, 'completion', None) or getattr(message, 'completion_text', '')
        if not response_text:
            warnings.warn("Couldn't extract completion text from Claude response")
            response_text = ""

        # Count tokens
        usage = getattr(message, 'usage', None)
        if usage:
            tokens_used = getattr(usage, 'prompt_tokens', 0) + getattr(usage, 'completion_tokens', 0)
        else:
            tokens_used = len(response_text.split())

        return response_text, tokens_used

    @property
    def name(self) -> str:
        return "claude"

    @property
    def supports_streaming(self) -> bool:
        return True
