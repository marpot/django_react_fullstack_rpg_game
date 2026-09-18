"""Immutable domain description of an adventure.

This module deliberately contains configuration only. Runtime values remain in
``RoomState`` and are not copied into these DTOs.
"""

from dataclasses import dataclass, replace
from typing import Any


@dataclass(frozen=True)
class ChoiceDefinition:
    id: int
    title: str
    description: str
    next_location_id: int | None
    effects: tuple[tuple[str, Any], ...] = ()


@dataclass(frozen=True)
class LocationDefinition:
    id: int
    title: str
    description: str
    order: int
    exits: tuple[ChoiceDefinition, ...] = ()


@dataclass(frozen=True)
class EnemyDefinition:
    id: str
    name: str
    hp: int
    defense: int
    attack_bonus: int
    damage_die: int
    damage_bonus: int
    location_id: int | None


@dataclass(frozen=True)
class NPCDefinition:
    id: str
    name: str
    dialog: tuple[str, ...]
    personality: str
    location_id: int | None


@dataclass(frozen=True)
class ProgressionStep:
    stage: str
    trigger: str
    objective: str
    next_stage: str | None


@dataclass(frozen=True)
class ProgressionDefinition:
    steps: tuple[ProgressionStep, ...]


@dataclass(frozen=True)
class AdventureDefinition:
    adventure_id: int
    title: str
    description: str
    start_location_id: int | None
    locations: tuple[LocationDefinition, ...]
    enemies: tuple[EnemyDefinition, ...]
    npcs: tuple[NPCDefinition, ...]
    progression: ProgressionDefinition


def _effects(value: dict | None) -> tuple[tuple[str, Any], ...]:
    return tuple(sorted((value or {}).items()))


def build_adventure_definition(adventure) -> AdventureDefinition:
    """Build a definition from the existing persistent world records.

    The builder reads Django models and static NPC definitions only; it does
    not access or mutate a room or any runtime state.
    """
    from game.npc.npc_registry import NPCRegistry
    if isinstance(adventure, (int, str)):
        from world.models import Adventure
        adventure = Adventure.objects.get(pk=adventure)

    locations = tuple(
        LocationDefinition(
            id=location.id,
            title=location.title,
            description=location.description,
            order=location.order,
            exits=tuple(
                ChoiceDefinition(
                    id=choice.id,
                    title=choice.title,
                    description=choice.description,
                    next_location_id=choice.next_location_id,
                    effects=_effects(choice.effects),
                )
                for choice in location.choices.select_related("next_location").order_by("id")
            ),
        )
        for location in adventure.locations.order_by("order", "id")
    )
    start_location_id = locations[0].id if locations else None

    enemies = tuple(
        EnemyDefinition(
            id=enemy.name.lower().strip(),
            name=enemy.name,
            hp=enemy.hp,
            defense=enemy.defense,
            attack_bonus=enemy.attack_bonus,
            damage_die=getattr(enemy, "damage_die", 6),
            damage_bonus=getattr(enemy, "damage_bonus", 0),
            location_id=None,
        )
        for enemy in adventure.enemies.order_by("id")
    )

    npc_definitions = tuple(
        NPCDefinition(
            id=npc.id,
            name=npc.name,
            dialog=tuple(npc.dialog),
            personality=npc.personality,
            location_id=None,
        )
        for npc in NPCRegistry.get_npcs_for_adventure(adventure.id)
    )

    return AdventureDefinition(
        adventure_id=adventure.id,
        title=adventure.title,
        description=adventure.description,
        start_location_id=start_location_id,
        locations=locations,
        enemies=enemies,
        npcs=npc_definitions,
        progression=ProgressionDefinition(steps=()),
    )


def build_cienie_eldorii_definition(adventure) -> AdventureDefinition:
    """Build the reference adventure configuration for Cienie Eldorii."""
    definition = build_adventure_definition(adventure)
    location_by_title = {
        location.title.casefold(): location.id for location in definition.locations
    }
    village_id = location_by_title.get("village")
    forest_id = location_by_title.get("forest")

    npcs = (
        NPCDefinition(
            id="guard",
            name="Guard",
            dialog=("Strażnik wskazuje ścieżkę do mrocznego lasu.",),
            personality="vigilant",
            location_id=village_id,
        ),
        NPCDefinition(
            id="merchant",
            name="Merchant",
            dialog=("Kupiec czekał na kogoś, kto pokonał bestię.",),
            personality="relieved",
            location_id=forest_id,
        ),
    )

    enemies = tuple(replace(enemy, location_id=forest_id) for enemy in definition.enemies)

    progression = ProgressionDefinition(
        steps=(
            ProgressionStep("forest", "talk:guard@village", "Pokonaj przeciwnika w lesie", "merchant"),
            ProgressionStep("merchant", "defeat:enemy@forest", "Odnajdź kupca w lesie", "return"),
            ProgressionStep("return", "talk:merchant@forest", "Wróć do wioski", "completed"),
            ProgressionStep("completed", "move:village", "", None),
        )
    )
    return replace(
        definition,
        enemies=enemies,
        npcs=npcs,
        progression=progression,
    )


def build_definition_for_adventure(adventure) -> AdventureDefinition:
    """Build the configured definition for a persisted adventure."""
    if isinstance(adventure, (int, str)):
        from world.models import Adventure
        adventure = Adventure.objects.get(pk=adventure)

    if adventure.title == "Cienie Eldorii":
        return build_cienie_eldorii_definition(adventure)
    return build_adventure_definition(adventure)
