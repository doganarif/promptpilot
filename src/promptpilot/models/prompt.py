"""
Core models for prompts and test cases.
"""

from dataclasses import dataclass, field
from typing import Dict, Any, Optional
from datetime import datetime


@dataclass
class Prompt:
    """
    Represents a prompt template with metadata.

    Attributes:
        name: Name of the prompt
        template: The prompt template string with placeholders
        version: Version number of the prompt
        created_at: When the prompt was created
        description: Optional description of the prompt
        metadata: Additional metadata as key-value pairs
    """
    name: str
    template: str
    version: int = 1
    created_at: datetime = field(default_factory=datetime.now)
    description: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def format(self, **variables) -> str:
        """
        Format the prompt template with the provided variables.

        Args:
            **variables: Variables to insert into the template

        Returns:
            Formatted prompt string
        """
        return self.template.format(**variables)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert prompt to dictionary representation.

        Returns:
            Dictionary representation of the prompt
        """
        return {
            "name": self.name,
            "template": self.template,
            "version": self.version,
            "created_at": self.created_at.isoformat(),
            "description": self.description,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'Prompt':
        """
        Create a Prompt instance from a dictionary.

        Args:
            data: Dictionary containing prompt data

        Returns:
            Prompt instance
        """
        # Convert ISO format string back to datetime if needed
        if "created_at" in data and isinstance(data["created_at"], str):
            data["created_at"] = datetime.fromisoformat(data["created_at"])

        return cls(**data)


@dataclass
class TestCase:
    """
    Represents a test case for prompt testing.

    Attributes:
        name: Identifier for the test case
        variables: Variables to insert into the prompt template
        description: Human-readable description of the test case
        metadata: Additional metadata as key-value pairs
    """
    name: str
    variables: Dict[str, str]
    description: Optional[str] = None
    metadata: Dict[str, Any] = field(default_factory=dict)

    def to_dict(self) -> Dict[str, Any]:
        """
        Convert test case to dictionary representation.

        Returns:
            Dictionary representation of the test case
        """
        return {
            "name": self.name,
            "variables": self.variables,
            "description": self.description,
            "metadata": self.metadata
        }

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> 'TestCase':
        """
        Create a TestCase instance from a dictionary.

        Args:
            data: Dictionary containing test case data

        Returns:
            TestCase instance
        """
        return cls(**data)
