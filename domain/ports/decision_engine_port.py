"""
Defines the interface (port) for AI decision-making services.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict


class DecisionEnginePort(ABC):
    """An abstract base class for AI-powered decision engines."""

    @abstractmethod
    def get_chat_completion(self, context: Dict[str, Any], instructions: str) -> str:
        """
        Gets a recommendation from the AI model based on the provided context
        and instructions.
        """
        raise NotImplementedError
