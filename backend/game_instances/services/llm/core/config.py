import math
import os
from dataclasses import dataclass


DEFAULT_GROQ_MODEL = "openai/gpt-oss-120b"
DEFAULT_TIMEOUT_SECONDS = 10.0
PROVIDER_NAMES = frozenset({"groq", "openrouter", "ollama"})


class LLMConfigurationError(ValueError):
    pass


@dataclass(frozen=True)
class LLMConfig:
    provider: str
    model: str
    timeout_seconds: float

    @classmethod
    def from_env(cls):
        provider = (os.getenv("LLM_PROVIDER") or "groq").strip().lower()
        if provider not in PROVIDER_NAMES:
            raise LLMConfigurationError(
                f"Unsupported LLM_PROVIDER: {provider!r}. Choose groq, openrouter or ollama."
            )

        model = (os.getenv("LLM_MODEL") or "").strip()
        if not model:
            if provider != "groq":
                raise LLMConfigurationError(f"LLM_MODEL is required for {provider}.")
            model = DEFAULT_GROQ_MODEL

        raw_timeout = os.getenv("LLM_TIMEOUT_SECONDS") or str(DEFAULT_TIMEOUT_SECONDS)
        try:
            timeout = float(raw_timeout)
        except ValueError as exc:
            raise LLMConfigurationError("LLM_TIMEOUT_SECONDS must be a positive number.") from exc
        if not math.isfinite(timeout) or timeout <= 0:
            raise LLMConfigurationError("LLM_TIMEOUT_SECONDS must be a positive number.")

        return cls(provider=provider, model=model, timeout_seconds=timeout)
