"""
Provider implementations for different AI backends.
"""

from .base import BaseProvider
from .openai_provider import OpenAIProvider
from .claude_provider import ClaudeProvider
from .llama_provider import LlamaProvider
from .hf_provider import HFProvider


def get_provider(provider_name: str = None, model: str = None) -> BaseProvider:
    """
    Get an instance of the specified provider.

    Args:
        provider_name: Name of the provider to use (openai, claude, llama, hf)
        model: Specific model to use with the provider

    Returns:
        An instance of the appropriate provider

    Raises:
        ValueError: If the provider name is not recognized
    """
    provider_name = provider_name.lower() if provider_name else 'openai'

    if provider_name == 'openai':
        return OpenAIProvider(model=model)
    elif provider_name == 'claude':
        return ClaudeProvider(model=model)
    elif provider_name == 'llama':
        return LlamaProvider(model=model)
    elif provider_name == 'hf':
        return HFProvider(model_name=model)
    else:
        raise ValueError(f"Unsupported provider: {provider_name}")


__all__ = ["BaseProvider", "OpenAIProvider", "ClaudeProvider", 'LlamaProvider', "HFProvider", "get_provider"]
