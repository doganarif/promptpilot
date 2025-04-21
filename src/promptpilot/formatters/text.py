"""
Text formatter for human-readable output.
"""

import sys
from typing import Dict, Any, Optional, TextIO

from .base import BaseFormatter


class TextFormatter(BaseFormatter):
    """
    Formatter for human-readable text output.
    """

    def __init__(self, include_responses: bool = True, output: Optional[TextIO] = None):
        """
        Initialize the text formatter.

        Args:
            include_responses: Whether to include full response texts in output
            output: Output stream (defaults to sys.stdout)
        """
        self.include_responses = include_responses
        self.output = output or sys.stdout

    def format_output(self, result: Dict[str, Any]) -> None:
        """
        Format and print test results.

        Args:
            result: Dictionary containing test results
        """
        formatted = self.format_to_string(result)
        print(formatted, file=self.output)

    def format_to_string(self, result: Dict[str, Any]) -> str:
        """
        Format test results to a string representation.

        Args:
            result: Dictionary containing test results

        Returns:
            Formatted string representation of the results
        """
        result_type = result.get('type', '')

        if result_type == 'abtest_result':
            return self._format_abtest_result(result)
        elif result_type == 'multi_prompt_result':
            return self._format_multi_prompt_result(result)
        elif result_type == 'batch_test_result':
            return self._format_batch_test_result(result)
        elif 'error' in result:
            return self._format_error(result)
        else:
            # Generic output
            lines = ["Test Results:"]
            for key, value in result.items():
                if key != 'type':
                    lines.append(f"{key}: {value}")
            return "\n".join(lines)

    def _format_abtest_result(self, result: Dict[str, Any]) -> str:
        """Format A/B test results"""
        lines = [
            "=" * 50,
            "A/B TEST RESULTS",
            "=" * 50,
            f"Provider: {result.get('provider', 'Unknown')}",
            ""
        ]

        # Variant A info
        if 'prompt_a' in result:
            variant_a = result['prompt_a']
            lines.append(f"VARIANT A: {variant_a.get('name', 'Prompt A')}")
            if 'template' in variant_a:
                lines.append("Template:")
                for line in variant_a['template'].splitlines():
                    lines.append(f"  {line}")
            lines.append(f"Tokens: {variant_a.get('tokens', 'N/A')}")
            if self.include_responses and 'response' in variant_a:
                lines.append("\nResponse:")
                lines.append(variant_a['response'])
            lines.append("")

        # Variant B info
        if 'prompt_b' in result:
            variant_b = result['prompt_b']
            lines.append(f"VARIANT B: {variant_b.get('name', 'Prompt B')}")
            if 'template' in variant_b:
                lines.append("Template:")
                for line in variant_b['template'].splitlines():
                    lines.append(f"  {line}")
            lines.append(f"Tokens: {variant_b.get('tokens', 'N/A')}")
            if self.include_responses and 'response' in variant_b:
                lines.append("\nResponse:")
                lines.append(variant_b['response'])
            lines.append("")

        # Results summary
        lines.append("=" * 50)
        lines.append("RESULTS SUMMARY")
        lines.append(f"Winner: Variant {result.get('winner', 'Unknown')}")
        if 'token_difference' in result:
            lines.append(f"Token difference: {result['token_difference']}")
        if 'token_percent' in result:
            lines.append(f"Savings percentage: {result['token_percent']}%")
        if 'reason' in result:
            lines.append(f"Reason: {result['reason']}")

        return "\n".join(lines)

    def _format_multi_prompt_result(self, result: Dict[str, Any]) -> str:
        """Format multi-prompt test results"""
        lines = [
            "=" * 50,
            "MULTI-PROMPT TEST RESULTS",
            "=" * 50,
            f"Provider: {result.get('provider', 'Unknown')}",
            f"Prompts tested: {result.get('prompts_tested', 0)}",
            ""
        ]

        # Individual prompt results
        if 'results' in result:
            lines.append("INDIVIDUAL RESULTS:")
            sorted_results = sorted(
                result['results'].items(),
                key=lambda x: x[1].get('tokens', float('inf'))
            )

            for name, data in sorted_results:
                lines.append(f"\nPrompt: {name}")
                if 'template' in data:
                    lines.append("Template:")
                    for line in data['template'].splitlines():
                        lines.append(f"  {line}")
                lines.append(f"Tokens: {data.get('tokens', 'N/A')}")
                if self.include_responses and 'response' in data:
                    lines.append("\nResponse:")
                    lines.append(data['response'])

        if 'winner' in result:
            winner = result['winner']
            lines.append("\n" + "=" * 50)
            lines.append("WINNER")
            lines.append(f"Most efficient prompt: {winner.get('name', 'Unknown')}")
            lines.append(f"Token count: {winner.get('tokens', 'N/A')}")

        return "\n".join(lines)

    def _format_batch_test_result(self, result: Dict[str, Any]) -> str:
        """Format batch test results"""
        lines = [
            "=" * 50,
            "BATCH TEST RESULTS",
            "=" * 50,
            f"Provider: {result.get('provider', 'Unknown')}",
            f"Test cases: {result.get('test_cases', 0)}",
            ""
        ]

        if 'case_results' in result:
            lines.append("CASE RESULTS:")

            for name, data in result['case_results'].items():
                lines.append(f"\nCase: {name}")
                if data.get('description'):
                    lines.append(f"Description: {data['description']}")
                lines.append(f"Input length: {data.get('input_length', 'N/A')} words")
                if 'A' in data:
                    lines.append(
                        f"Variant A ({data['A'].get('prompt_name', 'Prompt A')}) tokens: {data['A'].get('tokens', 'N/A')}"
                    )
                if 'B' in data:
                    lines.append(
                        f"Variant B ({data['B'].get('prompt_name', 'Prompt B')}) tokens: {data['B'].get('tokens', 'N/A')}"
                    )
                lines.append(
                    f"Winner: Variant {data.get('winner', 'Unknown')} (saves {data.get('token_difference', 'N/A')} tokens, {data.get('savings_percent', 'N/A')}%)"
                )
                if self.include_responses:
                    if 'A' in data and 'response' in data['A']:
                        lines.append("\nVariant A response:")
                        lines.append(data['A']['response'])
                    if 'B' in data and 'response' in data['B']:
                        lines.append("\nVariant B response:")
                        lines.append(data['B']['response'])

        lines.append("\n" + "=" * 50)
        lines.append("OVERALL RESULTS")
        if 'prompt_a' in result:
            pa = result['prompt_a']
            lines.append(f"Prompt A ({pa.get('name')}) wins: {pa.get('wins', 0)}")
        if 'prompt_b' in result:
            pb = result['prompt_b']
            lines.append(f"Prompt B ({pb.get('name')}) wins: {pb.get('wins', 0)}")
        lines.append(f"Overall winner: Variant {result.get('overall_winner', 'Unknown')}")

        return "\n".join(lines)

    def _format_error(self, result: Dict[str, Any]) -> str:
        """Format error message"""
        return f"Error: {result.get('error', 'Unknown error')}"
