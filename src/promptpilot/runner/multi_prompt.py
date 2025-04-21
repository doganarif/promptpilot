"""
Multi-prompt test runner for comparing multiple prompt variants.
"""

from typing import Dict, Any, Optional, List

from ..providers.base import BaseProvider
from ..models.prompt import Prompt
from ..formatters import TextFormatter, BaseFormatter


class MultiPromptTestRunner:
    """
    Runner for testing multiple prompt variants.
    """

    def __init__(
            self,
            provider: BaseProvider,
            formatter: Optional[BaseFormatter] = None
    ):
        """
        Initialize the multi-prompt test runner.

        Args:
            provider: Provider to use for testing
            formatter: Output formatter (defaults to TextFormatter)
        """
        self.provider = provider
        self.formatter = formatter or TextFormatter()

    def run_test(
            self,
            prompts: List[Prompt],
            variables: Dict[str, str],
            include_responses: bool = False
    ) -> Dict[str, Any]:
        """
        Run a test comparing multiple prompts.

        Args:
            prompts: List of prompts to test
            variables: Variables to insert into prompt templates
            include_responses: Whether to include response texts in results

        Returns:
            Dictionary with test results
        """
        if len(prompts) < 2:
            raise ValueError("At least two prompts are required for testing")

        # Track results for each prompt
        prompt_results = {}

        # Test each prompt
        for prompt in prompts:
            # Format prompt with variables
            formatted = prompt.format(**variables)

            # Send to provider
            text, tokens = self.provider.send_prompt(formatted)

            # Store results
            prompt_results[prompt.name] = {
                "tokens": tokens,
                "prompt_template": prompt.template,
                "prompt_version": prompt.version
            }

            if include_responses:
                prompt_results[prompt.name]["response"] = text

        # Find the winner (lowest token count)
        winner_name = min(prompt_results.items(), key=lambda x: x[1]["tokens"])[0]
        winner_tokens = prompt_results[winner_name]["tokens"]

        # Prepare result data
        result = {
            "type": "multi_prompt_result",
            "provider": self.provider.name,
            "prompts_tested": len(prompts),
            "results": prompt_results,
            "winner": {
                "name": winner_name,
                "tokens": winner_tokens
            }
        }

        return result

    def display_results(self, result: Dict[str, Any]) -> None:
        """
        Display test results using the configured formatter.

        Args:
            result: Dictionary with test results
        """
        self.formatter.format_output(result)

    def get_winner(self, result: Dict[str, Any]) -> Prompt:
        """
        Get the winning prompt.

        Args:
            result: Dictionary with test results

        Returns:
            The winning Prompt object
        """
        winner_name = result["winner"]["name"]
        winner_data = result["results"][winner_name]

        return Prompt(
            name=winner_name,
            template=winner_data["prompt_template"],
            version=winner_data.get("prompt_version", 1)
        )

    def get_ranked_prompts(self, result: Dict[str, Any]) -> List[str]:
        """
        Get prompt names ranked by token efficiency.

        Args:
            result: Dictionary with test results

        Returns:
            List of prompt names, from most to least efficient
        """
        sorted_results = sorted(
            result["results"].items(),
            key=lambda x: x[1]["tokens"]
        )
        return [name for name, _ in sorted_results]
