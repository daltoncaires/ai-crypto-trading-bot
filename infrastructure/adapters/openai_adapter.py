"""Adapter for the OpenAI API."""

from __future__ import annotations

import time
from typing import Any, Dict

from openai import APIError, OpenAI

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
        Gets a recommendation from the AI model, with performance logging.
        """
        start_time = time.monotonic()
        try:
            logger.debug(f"Sending context to OpenAI: {context}")
            response = self.client.chat.completions.create(
                model=model,
                messages=[
                    {"role": "system", "content": instructions},
                    {"role": "user", "content": str(context)},
                ],
            )
            duration = time.monotonic() - start_time
            recommendation = response.choices[0].message.content
            logger.info(
                "OpenAI API call successful",
                extra={
                    "event": "api_call",
                    "adapter": "openai",
                    "model": model,
                    "duration_ms": duration * 1000,
                },
            )
            logger.debug(f"Received recommendation from OpenAI: {recommendation}")
            return recommendation or "NEUTRAL"
        except APIError as e:
            duration = time.monotonic() - start_time
            logger.error(
                f"OpenAI API error: {e}",
                extra={
                    "event": "api_error",
                    "adapter": "openai",
                    "model": model,
                    "duration_ms": duration * 1000,
                },
            )
            return "NEUTRAL"
        except Exception as e:
            duration = time.monotonic() - start_time
            logger.error(
                f"An unexpected error occurred with OpenAI service: {e}",
                extra={
                    "event": "unexpected_error",
                    "adapter": "openai",
                    "duration_ms": duration * 1000,
                },
            )
            return "NEUTRAL"
