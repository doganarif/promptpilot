"""
JSON formatter for machine-readable output.
"""

import json
import sys
from typing import Dict, Any, Optional, TextIO
from datetime import datetime

from .base import BaseFormatter


class JSONFormatter(BaseFormatter):
    """
    Formatter for JSON output.
    """

    def __init__(
            self,
            include_responses: bool = False,
            output: Optional[TextIO] = None,
            indent: Optional[int] = 2,
            include_metadata: bool = True
    ):
        """
        Initialize the JSON formatter.

        Args:
            include_responses: Whether to include full response texts in output
            output: Output stream (defaults to sys.stdout)
            indent: JSON indentation level (None for compact JSON)
            include_metadata: Whether to include timestamp and version metadata
        """
        self.include_responses = include_responses
        self.output = output or sys.stdout
        self.indent = indent
        self.include_metadata = include_metadata

    def format_output(self, result: Dict[str, Any]) -> None:
        """
        Format and print test results as JSON.

        Args:
            result: Dictionary containing test results
        """
        json_str = self.format_to_string(result)
        print(json_str, file=self.output)

    def format_to_string(self, result: Dict[str, Any]) -> str:
        """
        Format test results to a JSON string.

        Args:
            result: Dictionary containing test results

        Returns:
            JSON string representation of the results
        """
        # Make a deep copy to avoid modifying the original
        output_data = self._process_result(result)

        # Add metadata if requested
        if self.include_metadata:
            output_data["metadata"] = {
                "timestamp": datetime.now().isoformat()
            }

        # Convert to JSON string
        return json.dumps(output_data, indent=self.indent)

    def _process_result(self, result: Dict[str, Any]) -> Dict[str, Any]:
        """
        Process the result data for JSON output.

        Args:
            result: Dictionary containing test results

        Returns:
            Processed dictionary ready for JSON conversion
        """
        # Create a new dictionary to avoid modifying the original
        processed: Dict[str, Any] = {}

        # Copy all fields
        for key, value in result.items():
            processed[key] = value

        # Process nested dictionaries and lists
        for key in list(processed.keys()):
            if isinstance(processed[key], dict):
                processed[key] = self._process_dict(processed[key])
            elif isinstance(processed[key], list):
                processed[key] = self._process_list(processed[key])

        # Remove response texts if not requested
        if not self.include_responses:
            self._remove_responses(processed)

        return processed

    def _process_dict(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """Process a nested dictionary"""
        processed: Dict[str, Any] = {}

        for key, value in data.items():
            if isinstance(value, dict):
                processed[key] = self._process_dict(value)
            elif isinstance(value, list):
                processed[key] = self._process_list(value)
            else:
                processed[key] = value

        return processed

    def _process_list(self, data: list) -> list:
        """Process a nested list"""
        processed: list = []

        for item in data:
            if isinstance(item, dict):
                processed.append(self._process_dict(item))
            elif isinstance(item, list):
                processed.append(self._process_list(item))
            else:
                processed.append(item)

        return processed

    def _remove_responses(self, data: Dict[str, Any]) -> None:
        """Remove response texts from the data structure"""
        result_type = data.get('type', '')

        if result_type == 'abtest_result':
            if 'prompt_a' in data and 'response' in data['prompt_a']:
                del data['prompt_a']['response']
            if 'prompt_b' in data and 'response' in data['prompt_b']:
                del data['prompt_b']['response']

        elif result_type == 'multi_prompt_result':
            if 'results' in data:
                for prompt_data in data['results'].values():
                    if 'response' in prompt_data:
                        del prompt_data['response']

        elif result_type == 'batch_test_result':
            if 'case_results' in data:
                for case_data in data['case_results'].values():
                    if 'A' in case_data and 'response' in case_data['A']:
                        del case_data['A']['response']
                    if 'B' in case_data and 'response' in case_data['B']:
                        del case_data['B']['response']

        # Handle nested structures
        for key, value in data.items():
            if isinstance(value, dict):
                self._remove_responses(value)
            elif isinstance(value, list):
                for item in value:
                    if isinstance(item, dict):
                        self._remove_responses(item)
