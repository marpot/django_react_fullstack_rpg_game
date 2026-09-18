import json

from game.domain.generated_adventure import (
    GeneratedAdventureSpec,
    GeneratedChoiceSpec,
    GeneratedEnemySpec,
    GeneratedLocationSpec,
    GeneratedNPCSpec,
    GeneratedProgressionStep,
    validate_generated_adventure,
)
from game_instances.services.llm.core.llm_client import LLMClient


class GeneratedAdventureGenerationError(ValueError):
    """The provider response is not a generated adventure JSON document."""


SYSTEM_PROMPT = """Return ONLY JSON for a generated adventure.
Use exactly these top-level fields: title, description, start_location,
locations, choices, enemies, npcs, progression.
Do not include database IDs, runtime state, HP changes, turns, or commands.
"""


class GeneratedAdventureGenerator:
    def __init__(self, client=None):
        self.client = client or LLMClient()

    def generate(self, prompt: str) -> GeneratedAdventureSpec:
        raw = self.client.generate(
            SYSTEM_PROMPT,
            prompt,
        )
        try:
            payload = json.loads(raw)
            spec = self._spec_from_payload(payload)
        except (TypeError, ValueError, json.JSONDecodeError) as exc:
            if isinstance(exc, GeneratedAdventureGenerationError):
                raise
            raise GeneratedAdventureGenerationError(
                "LLM returned malformed adventure JSON."
            ) from exc

        return validate_generated_adventure(spec)

    @staticmethod
    def _spec_from_payload(payload) -> GeneratedAdventureSpec:
        if not isinstance(payload, dict):
            raise GeneratedAdventureGenerationError(
                "Adventure JSON must be an object."
            )

        try:
            return GeneratedAdventureSpec(
                title=payload["title"],
                description=payload["description"],
                start_location=payload["start_location"],
                locations=tuple(
                    GeneratedLocationSpec(**location)
                    for location in payload["locations"]
                ),
                choices=tuple(
                    GeneratedChoiceSpec(**choice)
                    for choice in payload["choices"]
                ),
                enemies=tuple(
                    GeneratedEnemySpec(**enemy)
                    for enemy in payload["enemies"]
                ),
                npcs=tuple(
                    GeneratedNPCSpec(**npc)
                    for npc in payload["npcs"]
                ),
                progression=tuple(
                    GeneratedProgressionStep(**step)
                    for step in payload["progression"]
                ),
            )
        except (KeyError, TypeError) as exc:
            raise GeneratedAdventureGenerationError(
                "Adventure JSON does not match the generated adventure schema."
            ) from exc
