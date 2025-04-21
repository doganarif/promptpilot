"""
Optimized provider module with lazy loading and better UX.
"""
import os
from typing import Optional, Dict, Any, Callable
import time
import sys

# Base provider class - lightweight, no external imports
class BaseProvider:
    """Abstract base class for AI providers."""

    def __init__(self):
        self._start_time = None

    def send_prompt(self, prompt: str):
        """Send a prompt to the AI provider and get a response."""
        raise NotImplementedError("Providers must implement send_prompt")

    @property
    def name(self) -> str:
        """Get the name of the provider."""
        raise NotImplementedError("Providers must implement name property")

    @property
    def supports_streaming(self) -> bool:
        """Whether this provider supports streaming responses."""
        return False

    def __str__(self) -> str:
        return self.name

    def _start_timing(self):
        """Start timing a request for metrics"""
        self._start_time = time.time()

    def _end_timing(self) -> float:
        """End timing and return elapsed time"""
        if self._start_time is None:
            return 0
        elapsed = time.time() - self._start_time
        self._start_time = None
        return elapsed


# Lazy importing providers
def get_provider(provider_name: Optional[str] = None,
                 model: Optional[str] = None,
                 progress_callback: Optional[Callable[[str], None]] = None) -> BaseProvider:
    """
    Get an instance of the specified provider with progress reporting.

    Args:
        provider_name: Name of the provider to use (openai, claude, llama, hf)
        model: Specific model to use with the provider
        progress_callback: Optional callback for reporting progress

    Returns:
        An instance of the appropriate provider
    """
    # Default progress reporter
    if progress_callback is None:
        def progress_callback(msg):
            sys.stdout.write(f"\r{msg}")
            sys.stdout.flush()

    provider_name = provider_name.lower() if provider_name else 'openai'

    # OpenAI provider
    if provider_name == 'openai':
        progress_callback("⚙️ Initializing OpenAI provider...")
        # Lazy import
        try:
            from .openai_provider import OpenAIProvider
            provider = OpenAIProvider(model=model)
            progress_callback(f"✅ OpenAI provider ready with model: {provider.model}")
            return provider
        except ImportError:
            progress_callback("🔄 Installing OpenAI package...")
            # Attempt auto-install if missing
            try:
                import subprocess
                subprocess.check_call([sys.executable, "-m", "pip", "install", "openai", "--quiet"])
                progress_callback("✅ OpenAI package installed")
                # Try again after install
                from .openai_provider import OpenAIProvider
                return OpenAIProvider(model=model)
            except Exception as e:
                progress_callback(f"❌ OpenAI provider failed: {e}")
                raise ValueError(f"Error initializing OpenAI provider: {e}")

    # Claude provider
    elif provider_name == 'claude':
        progress_callback("⚙️ Initializing Claude provider...")
        try:
            from .claude_provider import ClaudeProvider
            provider = ClaudeProvider(model=model)
            progress_callback(f"✅ Claude provider ready with model: {provider.model}")
            return provider
        except ImportError:
            progress_callback("🔄 Installing Anthropic package...")
            try:
                import subprocess
                subprocess.check_call([sys.executable, "-m", "pip", "install", "anthropic", "--quiet"])
                progress_callback("✅ Anthropic package installed")
                from .claude_provider import ClaudeProvider
                return ClaudeProvider(model=model)
            except Exception as e:
                progress_callback(f"❌ Claude provider failed: {e}")
                raise ValueError(f"Error initializing Claude provider: {e}")

    # Llama provider
    elif provider_name == 'llama':
        progress_callback("⚙️ Initializing Llama provider...")
        try:
            from .llama_provider import LlamaProvider
            provider = LlamaProvider(model=model)
            progress_callback(f"✅ Llama provider ready with model: {provider.model}")
            return provider
        except ImportError:
            progress_callback(f"❌ Llama provider failed - missing dependencies")
            raise ValueError("Error initializing Llama provider")

    # HuggingFace provider
    elif provider_name == 'hf':
        progress_callback("⚙️ Initializing HuggingFace provider...")
        progress_callback("⚠️ HuggingFace loading may take some time...")
        try:
            from .hf_provider import HFProvider
            provider = HFProvider(model_name=model)
            progress_callback(f"✅ HuggingFace provider ready with model: {model or 'gpt2'}")
            return provider
        except ImportError:
            progress_callback("🔄 Installing transformers package (this may take a while)...")
            try:
                import subprocess
                subprocess.check_call([sys.executable, "-m", "pip", "install", "transformers", "--quiet"])
                progress_callback("✅ Transformers package installed")
                from .hf_provider import HFProvider
                return HFProvider(model_name=model)
            except Exception as e:
                progress_callback(f"❌ HuggingFace provider failed: {e}")
                raise ValueError(f"Error initializing HuggingFace provider: {e}")

    else:
        raise ValueError(f"Unsupported provider: {provider_name}")


# Enhanced OpenAI provider with timing and progress feedback
class OpenAIProviderWithProgress(BaseProvider):
    """Provider implementation for OpenAI API with progress reporting."""

    def __init__(self, api_key: Optional[str] = None, model: Optional[str] = None,
                 progress_callback: Optional[Callable[[str], None]] = None):
        super().__init__()
        self.progress_callback = progress_callback or (lambda msg: None)

        # Initialization with progress feedback
        self.progress_callback("🔑 Checking API keys...")
        self.api_key = api_key or os.getenv('OPENAI_API_KEY')
        if not self.api_key:
            raise ValueError("OpenAI API key not found. Set the OPENAI_API_KEY environment variable.")

        # default to gpt-4 to match docs
        self.model = model or os.getenv('PROMPTCTL_DEFAULT_MODEL', 'gpt-4o')

        # Lazy import OpenAI
        self.progress_callback("📚 Loading OpenAI client...")
        try:
            from openai import OpenAI
            self.client = OpenAI(api_key=self.api_key)
            self.progress_callback(f"✅ OpenAI client initialized with model: {self.model}")
        except ImportError:
            self.progress_callback("❌ OpenAI package not found")
            raise ImportError("OpenAI package not installed. Run: pip install openai")

    def send_prompt(self, prompt: str):
        """Send prompt to OpenAI with progress reporting."""
        self.progress_callback(f"📤 Sending prompt to OpenAI ({self.model})...")
        self._start_timing()

        try:
            resp = self.client.chat.completions.create(
                model=self.model,
                messages=[{"role": "user", "content": prompt}]
            )
            elapsed = self._end_timing()

            response_text = resp.choices[0].message.content
            tokens = resp.usage.total_tokens

            self.progress_callback(f"📥 Received response ({tokens} tokens, {elapsed:.2f}s)")
            return response_text, tokens

        except Exception as e:
            self.progress_callback(f"❌ Error from OpenAI API: {e}")
            raise RuntimeError(f"OpenAI API error: {e}")

    @property
    def name(self) -> str:
        return "openai"

    @property
    def supports_streaming(self) -> bool:
        return True
