"""Wrapper around OpenAI's Responses API used by the bot."""

from __future__ import annotations

from openai import OpenAI

from utils.load_env import settings


class OpenAIService:
    def __init__(self):
        self.client = OpenAI(api_key=settings.openai_api_key)

    def get_chat_completion(
        self, data, instructions: str, model: str = "gpt-5-mini"
    ) -> str:
        response = self.client.responses.create(
            model=model, input=str(data), instructions=instructions
        )
        return response.output_text
