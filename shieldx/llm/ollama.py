from __future__ import annotations

import os
from typing import Any

from .base import BaseLLMClient


class OllamaClient(BaseLLMClient):
    """
    Ollama LLM provider - runs models locally for free.
    
    Requires Ollama to be installed and running.
    https://ollama.com
    """

    def __init__(
        self,
        model: str = "llama3.1",
        base_url: str = "http://localhost:11434/v1",
        api_key: str = "ollama",
        **kwargs: Any,
    ):
        self.model = model
        self.base_url = base_url
        self.api_key = api_key
        self.extra_kwargs = kwargs
        self._client = None

    def _get_client(self):
        if self._client is not None:
            return self._client

        try:
            from openai import OpenAI
        except ImportError:
            raise ImportError(
                "openai package required for Ollama. Install with: pip install openai"
            )

        self._client = OpenAI(
            base_url=self.base_url,
            api_key=self.api_key,
        )
        return self._client

    def generate(self, prompt: str, system_prompt: str | None = None, **kwargs) -> str:
        """
        Generate using Ollama.
        """
        client = self._get_client()

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                **{**self.extra_kwargs, **kwargs},
            )
        except Exception as exc:
            raise Exception(f"Ollama error: {exc}. Make sure Ollama is running (ollama serve)")

        content = response.choices[0].message.content
        return content or ""