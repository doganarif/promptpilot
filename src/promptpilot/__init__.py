"""
Optimized init file with lazy imports to improve startup time.
"""

# Define version
__version__ = "0.0.1"

# Minimal exports - no imports at the top level
__all__ = [
    "get_provider", "BaseProvider",
    "OpenAIProvider", "ClaudeProvider", "LlamaProvider", "HFProvider",
    "Prompt", "TestCase",
    "ABTestRunner", "MultiPromptTestRunner", "BatchTestRunner",
    "TextFormatter", "JSONFormatter"
]

# Lazy import functions
def get_provider(*args, **kwargs):
    """Lazy import and return a provider"""
    from .providers import get_provider as _get_provider
    return _get_provider(*args, **kwargs)

# Properties for lazy imports - these will only import when accessed
@property
def BaseProvider():
    from .providers.base import BaseProvider as _BaseProvider
    return _BaseProvider

@property
def OpenAIProvider():
    from .providers.openai_provider import OpenAIProvider as _OpenAIProvider
    return _OpenAIProvider

@property
def ClaudeProvider():
    from .providers.claude_provider import ClaudeProvider as _ClaudeProvider
    return _ClaudeProvider

@property
def LlamaProvider():
    from .providers.llama_provider import LlamaProvider as _LlamaProvider
    return _LlamaProvider

@property
def HFProvider():
    from .providers.hf_provider import HFProvider as _HFProvider
    return _HFProvider

@property
def Prompt():
    from .models.prompt import Prompt as _Prompt
    return _Prompt

@property
def TestCase():
    from .models.prompt import TestCase as _TestCase
    return _TestCase

@property
def ABTestRunner():
    from .runner.abtest import ABTestRunner as _ABTestRunner
    return _ABTestRunner

@property
def MultiPromptTestRunner():
    from .runner.multi_prompt import MultiPromptTestRunner as _MultiPromptTestRunner
    return _MultiPromptTestRunner

@property
def BatchTestRunner():
    from .runner.batch import BatchTestRunner as _BatchTestRunner
    return _BatchTestRunner

@property
def TextFormatter():
    from .formatters.text import TextFormatter as _TextFormatter
    return _TextFormatter

@property
def JSONFormatter():
    from .formatters.json import JSONFormatter as _JSONFormatter
    return _JSONFormatter
