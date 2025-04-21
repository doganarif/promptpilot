"""
Enhanced ABTestRunner with progress feedback and better UX.
"""
from typing import Dict, Any, Optional, Tuple, Callable
import sys
import time

from ..providers.base import BaseProvider
from ..models.prompt import Prompt
from ..formatters import TextFormatter, BaseFormatter


class ABTestRunner:
    """
    Runner for A/B testing two prompt variants with progress reporting.
    """

    def __init__(
            self,
            provider: BaseProvider,
            formatter: Optional[BaseFormatter] = None,
            progress_callback: Optional[Callable[[str], None]] = None
    ):
        """
        Initialize the A/B test runner.

        Args:
            provider: Provider to use for testing
            formatter: Output formatter (defaults to TextFormatter)
            progress_callback: Optional callback for reporting progress
        """
        self.provider = provider
        self.formatter = formatter or TextFormatter()
        self.progress_callback = progress_callback or self._default_progress

    def _default_progress(self, message: str) -> None:
        """Default progress reporter that prints to console"""
        sys.stdout.write(f"\r{message}")
        sys.stdout.flush()

    def _report_progress(self, message: str) -> None:
        """Report progress using the configured callback"""
        if self.progress_callback:
            self.progress_callback(message)

    def run_test(
            self,
            prompt_a: Prompt,
            prompt_b: Prompt,
            variables: Dict[str, str],
            include_responses: bool = True
    ) -> Dict[str, Any]:
        """
        Run an A/B test comparing two prompts with progress feedback.

        Args:
            prompt_a: First prompt variant
            prompt_b: Second prompt variant
            variables: Variables to insert into prompt templates
            include_responses: Whether to include response texts in results

        Returns:
            Dictionary with test results
        """
        # Format prompts with variables
        self._report_progress("Formatting prompt templates...")
        formatted_a = prompt_a.format(**variables)
        formatted_b = prompt_b.format(**variables)

        # Show progress for first prompt
        self._report_progress(f"Sending Variant A ({prompt_a.name}) to {self.provider.name}...")
        start_time_a = time.time()
        text_a, tokens_a = self.provider.send_prompt(formatted_a)
        elapsed_a = time.time() - start_time_a
        self._report_progress(f"Variant A completed in {elapsed_a:.2f}s, used {tokens_a} tokens")

        # Show progress for second prompt
        self._report_progress(f"Sending Variant B ({prompt_b.name}) to {self.provider.name}...")
        start_time_b = time.time()
        text_b, tokens_b = self.provider.send_prompt(formatted_b)
        elapsed_b = time.time() - start_time_b
        self._report_progress(f"Variant B completed in {elapsed_b:.2f}s, used {tokens_b} tokens")

        # Analyze results
        self._report_progress("Analyzing results...")

        # Determine winner based on token efficiency
        winner = 'A' if tokens_a < tokens_b else 'B'
        token_diff = abs(tokens_a - tokens_b)
        token_percent = round((token_diff / max(tokens_a, tokens_b)) * 100, 2)

        # Clear progress line
        self._report_progress("")
        sys.stdout.write("\r" + " " * 80 + "\r")  # Clear progress line

        # Prepare result data, now including the raw templates
        result = {
            'type': 'abtest_result',
            'provider': self.provider.name,
            'prompt_a': {
                'name': prompt_a.name,
                'tokens': tokens_a,
                'template': prompt_a.template.strip(),
                'time_taken': f"{elapsed_a:.2f}s"
            },
            'prompt_b': {
                'name': prompt_b.name,
                'tokens': tokens_b,
                'template': prompt_b.template.strip(),
                'time_taken': f"{elapsed_b:.2f}s"
            },
            'winner': winner,
            'token_difference': token_diff,
            'token_percent': token_percent,
            'reason': 'Lower token usage'
        }

        # Include full responses if requested
        if include_responses:
            result['prompt_a']['response'] = text_a
            result['prompt_b']['response'] = text_b

        return result

    def display_results(self, result: Dict[str, Any]) -> None:
        """
        Display test results using the configured formatter.

        Args:
            result: Dictionary with test results
        """
        self.formatter.format_output(result)

    def get_winner(self, result: Dict[str, Any]) -> Tuple[str, int]:
        """
        Get the winning prompt and its token count.

        Args:
            result: Dictionary with test results

        Returns:
            Tuple of (winner_name, token_count)
        """
        winner_key = 'prompt_a' if result['winner'] == 'A' else 'prompt_b'
        return result[winner_key]['name'], result[winner_key]['tokens']
