"""Adapter for the OpenAI API."""

from __future__ import annotations

from typing import Any, Dict

from openai import OpenAI, APIError

from domain.ports.decision_engine_port import DecisionEnginePort
from utils.load_env import settings
from utils.logger import get_logger

logger = get_logger(__name__)


class OpenAIAdapter(DecisionEnginePort):
    """An adapter for the OpenAI API that implements the DecisionEnginePort."""

    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)
        logger.info("OpenAI adapter initialized.")

    def get_chat_completion(
        self, context: Dict[str, Any], instructions: str, model: str = "gpt-4-mini"
    ) -> str:
        """
        Gets a recommendation from the AI model, with error handling.
        """
        try:
            logger.debug(f"Sending context to OpenAI: {context}")
            # Note: The 'responses' API is hypothetical. The standard is 'chat.completions'.
            # Assuming the original code's `client.responses.create` is a custom or
            # old version, we adapt to the modern standard `chat.completions.create`.
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": instructions},
                    {"role": "user", "content": str(context)},
                ],
            )
            recommendation = response.choices[0].message.content
            logger.debug(f"Received recommendation from OpenAI: {recommendation}")
            return recommendation or "NEUTRAL"
        except APIError as e:
            logger.error(f"OpenAI API error: {e}")
            # Return a safe, neutral recommendation on failure
            return "NEUTRAL"
        except Exception as e:
            logger.error(f"An unexpected error occurred with OpenAI service: {e}")
            return "NEUTRAL"
