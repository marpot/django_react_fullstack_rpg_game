from types import SimpleNamespace

import pytest

from game_instances.services.llm.core import provider as provider_module
from game_instances.services.llm.core.config import LLMConfig, LLMConfigurationError
from game_instances.services.llm.core.llm_client import LLMClient, create_provider
from game_instances.services.llm.core.provider import (
    GroqProvider, OllamaProvider, OpenRouterProvider,
)
from game_instances.services.llm.dialogue.npc_dialogue_service import NPCDialogueService
from game_instances.services.llm.narration_service.narration_service import NarrationService


@pytest.mark.parametrize("name,model,provider_class", [
    ("groq", "openai/gpt-oss-120b", GroqProvider),
    ("openrouter", "openrouter/free", OpenRouterProvider),
    ("ollama", "local-model", OllamaProvider),
])
def test_factory_selects_configured_provider(monkeypatch, name, model, provider_class):
    monkeypatch.setenv("LLM_PROVIDER", name)
    monkeypatch.setenv("LLM_MODEL", model)

    selected = create_provider()

    assert isinstance(selected, provider_class)
    assert selected.model == model


@pytest.mark.parametrize("value", ["abc", "", "GROQQ"])
def test_invalid_provider_raises_controlled_error(monkeypatch, value):
    monkeypatch.setenv("LLM_PROVIDER", value)
    if value == "":
        assert isinstance(create_provider(), GroqProvider)
    else:
        with pytest.raises(LLMConfigurationError, match="LLM_PROVIDER"):
            create_provider()


def test_groq_has_configurable_default_model(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "groq")
    monkeypatch.delenv("LLM_MODEL", raising=False)

    assert create_provider().model == "openai/gpt-oss-120b"


@pytest.mark.parametrize("name", ["openrouter", "ollama"])
def test_non_groq_provider_requires_model(monkeypatch, name):
    monkeypatch.setenv("LLM_PROVIDER", name)
    monkeypatch.delenv("LLM_MODEL", raising=False)

    with pytest.raises(LLMConfigurationError, match="LLM_MODEL"):
        create_provider()


@pytest.mark.parametrize("name,model,key_name,default_url", [
    ("groq", "groq-model", "GROQ_API_KEY", "https://api.groq.com/openai/v1"),
    ("openrouter", "openrouter/free", "OPENROUTER_API_KEY", "https://openrouter.ai/api/v1"),
    ("ollama", "local-model", None, "http://host.docker.internal:11434/v1"),
])
def test_provider_request_uses_model_base_url_and_timeout(
    monkeypatch, name, model, key_name, default_url,
):
    monkeypatch.setenv("LLM_PROVIDER", name)
    monkeypatch.setenv("LLM_MODEL", model)
    monkeypatch.setenv("LLM_TIMEOUT_SECONDS", "4.5")
    base_url_env = {
        "groq": "GROQ_API_BASE_URL",
        "openrouter": "OPENROUTER_API_BASE_URL",
        "ollama": "OLLAMA_BASE_URL",
    }[name]
    monkeypatch.delenv(base_url_env, raising=False)
    if key_name:
        monkeypatch.setenv(key_name, "fake-key")

    calls = []

    class FakeOpenAI:
        def __init__(self, **kwargs):
            calls.append(("client", kwargs))
            self.chat = SimpleNamespace(
                completions=SimpleNamespace(create=self.create),
            )

        def create(self, **kwargs):
            calls.append(("request", kwargs))
            return SimpleNamespace(choices=[SimpleNamespace(
                message=SimpleNamespace(content="Odpowiedź."),
            )])

    monkeypatch.setattr(provider_module, "OpenAI", FakeOpenAI)

    assert LLMClient().generate("system", "user") == "Odpowiedź."
    assert calls[0][1]["base_url"] == default_url
    assert calls[0][1]["timeout"] == 4.5
    assert calls[0][1]["max_retries"] == 0
    assert calls[1][1]["model"] == model
    assert calls[1][1]["messages"] == [
        {"role": "system", "content": "system"},
        {"role": "user", "content": "user"},
    ]


@pytest.mark.parametrize("name,key_name,url_env", [
    ("groq", "GROQ_API_KEY", "GROQ_API_BASE_URL"),
    ("openrouter", "OPENROUTER_API_KEY", "OPENROUTER_API_BASE_URL"),
    ("ollama", None, "OLLAMA_BASE_URL"),
])
def test_base_url_can_be_overridden(monkeypatch, name, key_name, url_env):
    monkeypatch.setenv("LLM_PROVIDER", name)
    monkeypatch.setenv("LLM_MODEL", "custom-model")
    monkeypatch.setenv(url_env, "http://example.test/v1")
    if key_name:
        monkeypatch.setenv(key_name, "fake-key")
    captured = {}

    class FakeOpenAI:
        def __init__(self, **kwargs):
            captured.update(kwargs)
            self.chat = SimpleNamespace(completions=SimpleNamespace(
                create=lambda **kwargs: SimpleNamespace(choices=[SimpleNamespace(
                    message=SimpleNamespace(content="ok"),
                )]),
            ))

    monkeypatch.setattr(provider_module, "OpenAI", FakeOpenAI)
    LLMClient().generate("system", "user")

    assert captured["base_url"] == "http://example.test/v1"


@pytest.mark.parametrize("value", ["0", "-1", "NaN", "abc"])
def test_invalid_timeout_is_rejected(monkeypatch, value):
    monkeypatch.setenv("LLM_PROVIDER", "groq")
    monkeypatch.setenv("LLM_TIMEOUT_SECONDS", value)

    with pytest.raises(LLMConfigurationError, match="LLM_TIMEOUT_SECONDS"):
        LLMConfig.from_env()


def test_injected_provider_bypasses_factory(monkeypatch):
    import game_instances.services.llm.core.llm_client as client_module

    monkeypatch.setattr(client_module, "create_provider", lambda: pytest.fail("factory called"))
    fake = SimpleNamespace(complete=lambda system, user: "fake")

    assert LLMClient(provider=fake).generate("system", "user") == "fake"


@pytest.mark.parametrize("name,key_name", [
    ("groq", "GROQ_API_KEY"),
    ("openrouter", "OPENROUTER_API_KEY"),
])
def test_missing_cloud_key_fails_only_on_use(monkeypatch, name, key_name):
    monkeypatch.setenv("LLM_PROVIDER", name)
    monkeypatch.setenv("LLM_MODEL", "test-model")
    monkeypatch.delenv(key_name, raising=False)
    monkeypatch.setattr(provider_module, "OpenAI", lambda **kwargs: pytest.fail("HTTP client created"))

    client = LLMClient()
    with pytest.raises(LLMConfigurationError, match=key_name):
        client.generate("system", "user")


def test_missing_cloud_key_preserves_narration_and_dialogue_fallbacks(monkeypatch):
    monkeypatch.setenv("LLM_PROVIDER", "groq")
    monkeypatch.setenv("LLM_MODEL", "test-model")
    monkeypatch.delenv("GROQ_API_KEY", raising=False)
    monkeypatch.setattr(provider_module, "OpenAI", lambda **kwargs: pytest.fail("HTTP client created"))

    narration = NarrationService().event({
        "event_type": "move", "result": {"location": "crypt"},
    })
    dialogue = NPCDialogueService().generate({"npc_name": "Guide"})

    assert narration == "Przemieszczasz się do: crypt."
    assert dialogue == "Guide spogląda na ciebie uważnie, ale nie odpowiada."
