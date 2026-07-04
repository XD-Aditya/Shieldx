from __future__ import annotations

from shieldx.exceptions import LLMProviderError
from shieldx.llm.base import BaseLLMClient


class OpenAIClient(BaseLLMClient):
    def __init__(self, api_key: str | None = None, model: str = "gpt-4o-mini"):
        self.api_key = api_key
        self.model = model
        self._client = None

    def _get_client(self):
        if self._client is not None:
            return self._client

        try:
            from openai import OpenAI
        except ImportError as exc:
            raise LLMProviderError(
                "openai package is not installed. Run: pip install openai"
            ) from exc

        self._client = OpenAI(api_key=self.api_key)
        return self._client

    def generate(self, prompt: str, system_prompt: str | None = None, **kwargs) -> str:
        client = self._get_client()

        messages = []
        if system_prompt:
            messages.append({"role": "system", "content": system_prompt})
        messages.append({"role": "user", "content": prompt})

        try:
            response = client.chat.completions.create(
                model=self.model,
                messages=messages,
                **kwargs,
            )
        except Exception as exc:
            raise LLMProviderError(str(exc)) from exc

        content = response.choices[0].message.content
        if content is None:
            return ""

        if isinstance(content, str):
            return content

        return str(content)