"""Adapter for the OpenAI API."""

from __future__ import annotations

import time
from typing import Any, Dict

from openai import APIError, OpenAI
from tenacity import (
    retry,
    retry_if_exception_type,
    stop_after_attempt,
    wait_exponential,
)

from domain.ports.decision_engine_port import DecisionEnginePort
from utils.load_env import Settings
from utils.logger import get_logger

logger = get_logger(__name__)


class OpenAIAdapter(DecisionEnginePort):
    """An adapter for the OpenAI API that implements the DecisionEnginePort."""

    def __init__(self, config: Settings):
        self.config = config
        self.client = OpenAI(api_key=self.config.openai_api_key)
        logger.info("OpenAI adapter initialized.")

    def _get_retrying_api_call(self, api_call_func):
        @retry(
            stop=stop_after_attempt(self.config.api.max_retries),
            wait=wait_exponential(
                multiplier=self.config.api.retry_multiplier,
                min=self.config.api.retry_min_delay,
                max=self.config.api.rate_limit_sleep, # Using rate_limit_sleep as max delay for OpenAI too
            ),
            retry=retry_if_exception_type(APIError),
            reraise=True,
        )
        def _retrying_api_call(*args, **kwargs):
            return api_call_func(*args, **kwargs)
        return _retrying_api_call

    def get_chat_completion(
        self, context: Dict[str, Any], instructions: str, model: str = "gpt-4-mini"
    ) -> str:
        """
        Gets a recommendation from the AI model, with performance logging.
        """
        start_time = time.monotonic()
        try:
            logger.debug(f"Sending context to OpenAI: {context}")
            response = self._get_retrying_api_call(self.client.chat.completions.create)(
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
