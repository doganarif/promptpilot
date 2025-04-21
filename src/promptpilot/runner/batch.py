"""
Batch test runner for testing prompts across multiple inputs.
"""

from typing import Dict, Any, Optional, List

from ..providers.base import BaseProvider
from ..models.prompt import Prompt, TestCase
from ..formatters import TextFormatter, BaseFormatter


class BatchTestRunner:
    """
    Runner for batch testing prompts across multiple inputs.
    """

    def __init__(
            self,
            provider: BaseProvider,
            formatter: Optional[BaseFormatter] = None
    ):
        """
        Initialize the batch test runner.

        Args:
            provider: Provider to use for testing
            formatter: Output formatter (defaults to TextFormatter)
        """
        self.provider = provider
        self.formatter = formatter or TextFormatter()

    def run_batch_test(
            self,
            prompt_a: Prompt,
            prompt_b: Prompt,
            test_cases: List[TestCase],
            include_responses: bool = False
    ) -> Dict[str, Any]:
        """
        Run tests comparing two prompts across multiple test cases.

        Args:
            prompt_a: First prompt variant
            prompt_b: Second prompt variant
            test_cases: List of test cases to run
            include_responses: Whether to include response texts in results

        Returns:
            Dictionary with batch test results
        """
        # Track results for each test case
        case_results = {}

        # Test each input
        for case in test_cases:
            # Initialize results for this case
            case_results[case.name] = {
                "description": case.description,
                "input_length": len(''.join(case.variables.values()).split())
            }

            # Test both prompts on this input
            # Format prompts with variables
            formatted_a = prompt_a.format(**case.variables)
            formatted_b = prompt_b.format(**case.variables)

            # Send to provider
            text_a, tokens_a = self.provider.send_prompt(formatted_a)
            text_b, tokens_b = self.provider.send_prompt(formatted_b)

            # Store results for each variant
            case_results[case.name]["A"] = {
                "tokens": tokens_a,
                "prompt_name": prompt_a.name
            }

            case_results[case.name]["B"] = {
                "tokens": tokens_b,
                "prompt_name": prompt_b.name
            }

            if include_responses:
                case_results[case.name]["A"]["response"] = text_a
                case_results[case.name]["B"]["response"] = text_b

            # Determine winner for this test case
            winner = "A" if tokens_a < tokens_b else "B"
            token_diff = abs(tokens_a - tokens_b)
            token_percent = round((token_diff / max(tokens_a, tokens_b)) * 100, 2)

            case_results[case.name]["winner"] = winner
            case_results[case.name]["winner_name"] = prompt_a.name if winner == "A" else prompt_b.name
            case_results[case.name]["token_difference"] = token_diff
            case_results[case.name]["savings_percent"] = token_percent

        # Calculate overall stats
        prompt_a_wins = sum(1 for r in case_results.values() if r["winner"] == "A")
        prompt_b_wins = sum(1 for r in case_results.values() if r["winner"] == "B")
        overall_winner = "A" if prompt_a_wins > prompt_b_wins else "B"

        # Handle tie
        if prompt_a_wins == prompt_b_wins:
            # Determine by total tokens
            total_a = sum(r["A"]["tokens"] for r in case_results.values())
            total_b = sum(r["B"]["tokens"] for r in case_results.values())
            overall_winner = "A" if total_a < total_b else "B"

        # Prepare result data
        result = {
            "type": "batch_test_result",
            "provider": self.provider.name,
            "test_cases": len(test_cases),
            "prompt_a": {
                "name": prompt_a.name,
                "wins": prompt_a_wins
            },
            "prompt_b": {
                "name": prompt_b.name,
                "wins": prompt_b_wins
            },
            "overall_winner": overall_winner,
            "case_results": case_results
        }

        return result

    def display_results(self, result: Dict[str, Any]) -> None:
        """
        Display batch test results using the configured formatter.

        Args:
            result: Dictionary with batch test results
        """
        self.formatter.format_output(result)

    def get_overall_winner(self, result: Dict[str, Any]) -> Prompt:
        """
        Get the overall winning prompt.

        Args:
            result: Dictionary with batch test results

        Returns:
            The winning Prompt object
        """
        winner_key = "prompt_a" if result["overall_winner"] == "A" else "prompt_b"
        winner_name = result[winner_key]["name"]

        # Create a simple Prompt object with the winner info
        return Prompt(
            name=winner_name,
            template="",  # We don't have the template here
            version=1
        )

    def get_best_prompt_for_case(self, result: Dict[str, Any], case_name: str) -> str:
        """
        Get the best prompt for a specific test case.

        Args:
            result: Dictionary with batch test results
            case_name: Name of the test case

        Returns:
            Name of the best prompt for this case
        """
        if case_name not in result["case_results"]:
            raise ValueError(f"Test case '{case_name}' not found in results")

        return result["case_results"][case_name]["winner_name"]
