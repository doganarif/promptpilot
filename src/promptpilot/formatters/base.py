"""
Base formatter interface for test results.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any


class BaseFormatter(ABC):
    """
    Abstract base class for output formatters.

    All formatter implementations should inherit from this class
    and implement the required methods.
    """

    @abstractmethod
    def format_output(self, result: Dict[str, Any]) -> None:
        """
        Format and output test results.

        Args:
            result: Dictionary containing test results
        """
        pass

    @abstractmethod
    def format_to_string(self, result: Dict[str, Any]) -> str:
        """
        Format test results to a string representation.

        Args:
            result: Dictionary containing test results

        Returns:
            Formatted string representation of the results
        """
        pass

    def __str__(self) -> str:
        return self.__class__.__name__
