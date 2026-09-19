import os
from typing import Protocol

from openai import OpenAI

from game_instances.services.llm.core.config import LLMConfig, LLMConfigurationError


class LLMProvider(Protocol):
    def complete(self, system_prompt: str, user_prompt: str) -> str: ...


class _OpenAICompatibleProvider:
    api_key_env = None
    base_url_env = None
    default_base_url = None

    def __init__(self, config: LLMConfig | None = None):
        self.config = config or LLMConfig.from_env()
        self.model = self.config.model
        self._client = None

    def _api_key(self):
        if self.api_key_env is None:
            return "ollama"
        key = os.getenv(self.api_key_env)
        if not key:
            raise LLMConfigurationError(f"{self.api_key_env} is required for {self.config.provider}.")
        return key

    def complete(self, system_prompt: str, user_prompt: str) -> str:
        if self._client is None:
            self._client = OpenAI(
                api_key=self._api_key(),
                base_url=os.getenv(self.base_url_env) or self.default_base_url,
                timeout=self.config.timeout_seconds,
                max_retries=0,
            )
        response = self._client.chat.completions.create(
            model=self.model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            temperature=0.2,
            max_tokens=500,
        )
        return response.choices[0].message.content or ""


class GroqProvider(_OpenAICompatibleProvider):
    api_key_env = "GROQ_API_KEY"
    base_url_env = "GROQ_API_BASE_URL"
    default_base_url = "https://api.groq.com/openai/v1"


class OpenRouterProvider(_OpenAICompatibleProvider):
    api_key_env = "OPENROUTER_API_KEY"
    base_url_env = "OPENROUTER_API_BASE_URL"
    default_base_url = "https://openrouter.ai/api/v1"


class OllamaProvider(_OpenAICompatibleProvider):
    base_url_env = "OLLAMA_BASE_URL"
    default_base_url = "http://host.docker.internal:11434/v1"
