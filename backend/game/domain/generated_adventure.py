from dataclasses import dataclass


@dataclass(frozen=True)
class GeneratedLocationSpec:
    key: str
    title: str
    description: str


@dataclass(frozen=True)
class GeneratedChoiceSpec:
    title: str
    description: str
    from_location: str
    to_location: str


@dataclass(frozen=True)
class GeneratedEnemySpec:
    key: str
    name: str
    location: str
    hp: int = 30
    defense: int = 10
    attack_bonus: int = 2
    damage_die: int = 6
    damage_bonus: int = 1


@dataclass(frozen=True)
class GeneratedNPCSpec:
    key: str
    name: str
    role: str
    location: str


@dataclass(frozen=True)
class GeneratedProgressionStep:
    stage: str
    trigger: str
    objective: str
    next_stage: str | None


@dataclass(frozen=True)
class GeneratedAdventureSpec:
    title: str
    description: str
    start_location: str
    locations: tuple[GeneratedLocationSpec, ...]
    choices: tuple[GeneratedChoiceSpec, ...]
    enemies: tuple[GeneratedEnemySpec, ...]
    npcs: tuple[GeneratedNPCSpec, ...]
    progression: tuple[GeneratedProgressionStep, ...]


class GeneratedAdventureValidationError(ValueError):
    pass


def _parse_progression_trigger(trigger: str) -> tuple[str, str | None, str]:
    if ":" not in trigger:
        raise GeneratedAdventureValidationError(
            f"Unsupported progression trigger: {trigger}"
        )

    action, payload = trigger.split(":", 1)
    if action == "move" and payload and "@" not in payload:
        return action, None, payload

    if action in {"talk", "defeat"} and payload.count("@") == 1:
        target, location = payload.split("@", 1)
        if target and location:
            return action, target, location

    raise GeneratedAdventureValidationError(
        f"Unsupported progression trigger: {trigger}"
    )


def _location_is_reachable(
    start: str,
    destination: str,
    exits: dict[str, set[str]],
) -> bool:
    pending = [start]
    visited: set[str] = set()

    while pending:
        location = pending.pop()
        if location == destination:
            return True
        if location in visited:
            continue
        visited.add(location)
        pending.extend(exits.get(location, set()) - visited)

    return False


def validate_generated_adventure(
    spec: GeneratedAdventureSpec,
) -> GeneratedAdventureSpec:
    if not spec.title.strip():
        raise GeneratedAdventureValidationError("Adventure title is required.")

    if not spec.locations:
        raise GeneratedAdventureValidationError(
            "Adventure must contain at least one location."
        )

    location_keys = [location.key for location in spec.locations]

    if any(not key.strip() for key in location_keys):
        raise GeneratedAdventureValidationError(
            "Location keys cannot be empty."
        )

    if len(location_keys) != len(set(location_keys)):
        raise GeneratedAdventureValidationError(
            "Location keys must be unique."
        )

    known_locations = set(location_keys)
    location_by_title = {
        location.title.casefold(): location.key
        for location in spec.locations
    }

    if len(location_by_title) != len(spec.locations):
        raise GeneratedAdventureValidationError(
            "Location titles must be unique."
        )

    if spec.start_location not in known_locations:
        raise GeneratedAdventureValidationError(
            "Start location must reference an existing location."
        )

    for choice in spec.choices:
        if choice.from_location not in known_locations:
            raise GeneratedAdventureValidationError(
                f"Choice references unknown source location: "
                f"{choice.from_location}"
            )

        if choice.to_location not in known_locations:
            raise GeneratedAdventureValidationError(
                f"Choice references unknown target location: "
                f"{choice.to_location}"
            )

    enemy_keys: set[str] = set()

    for enemy in spec.enemies:
        if not enemy.key.strip():
            raise GeneratedAdventureValidationError(
                "Enemy keys cannot be empty."
            )

        if enemy.key in enemy_keys:
            raise GeneratedAdventureValidationError(
                f"Duplicate enemy key: {enemy.key}"
            )

        enemy_keys.add(enemy.key)

        if enemy.location not in known_locations:
            raise GeneratedAdventureValidationError(
                f"Enemy references unknown location: {enemy.location}"
            )

        if enemy.hp <= 0:
            raise GeneratedAdventureValidationError(
                f"Enemy HP must be positive: {enemy.key}"
            )

        if enemy.damage_die <= 0:
            raise GeneratedAdventureValidationError(
                f"Enemy damage die must be positive: {enemy.key}"
            )

    npc_keys: set[str] = set()
    npc_locations: dict[str, str] = {}

    for npc in spec.npcs:
        if not npc.key.strip():
            raise GeneratedAdventureValidationError(
                "NPC keys cannot be empty."
            )

        if npc.key in npc_keys:
            raise GeneratedAdventureValidationError(
                f"Duplicate NPC key: {npc.key}"
            )

        npc_keys.add(npc.key)
        npc_locations[npc.key] = npc.location

        if npc.location not in known_locations:
            raise GeneratedAdventureValidationError(
                f"NPC references unknown location: {npc.location}"
            )

    if not spec.progression:
        raise GeneratedAdventureValidationError(
            "Progression must contain at least one terminal path."
        )

    stages = [step.stage for step in spec.progression]

    if len(stages) != len(set(stages)):
        raise GeneratedAdventureValidationError(
            "Progression stages must be unique."
        )

    known_stages = set(stages)

    exits = {key: set() for key in known_locations}
    for choice in spec.choices:
        exits[choice.from_location].add(choice.to_location)

    current_location = spec.start_location
    defeated_locations: set[str] = set()

    for index, step in enumerate(spec.progression):
        if not step.stage.strip():
            raise GeneratedAdventureValidationError(
                "Progression stage cannot be empty."
            )

        if not step.trigger.strip():
            raise GeneratedAdventureValidationError(
                f"Progression trigger cannot be empty: {step.stage}"
            )

        if (
            step.next_stage is not None
            and step.next_stage not in known_stages
        ):
            raise GeneratedAdventureValidationError(
                f"Progression step references unknown next stage: "
                f"{step.next_stage}"
            )

        expected_next_stage = (
            spec.progression[index + 1].stage
            if index + 1 < len(spec.progression)
            else None
        )
        if step.next_stage != expected_next_stage:
            raise GeneratedAdventureValidationError(
                "Progression must form one ordered path ending in a "
                "terminal step."
            )

        action, target, location_title = _parse_progression_trigger(
            step.trigger
        )
        location_key = location_by_title.get(
            location_title.casefold()
        )
        if location_key is None:
            raise GeneratedAdventureValidationError(
                f"Progression trigger references unknown location: "
                f"{location_title}"
            )

        if action == "talk":
            if target not in npc_locations:
                raise GeneratedAdventureValidationError(
                    f"Progression trigger references unknown NPC: {target}"
                )
            if npc_locations[target] != location_key:
                raise GeneratedAdventureValidationError(
                    f"Progression trigger references NPC at wrong location: "
                    f"{target}"
                )
        elif action == "defeat":
            if target != "enemy":
                raise GeneratedAdventureValidationError(
                    "Defeat progression trigger must target 'enemy'."
                )
            if location_key not in {
                enemy.location for enemy in spec.enemies
            }:
                raise GeneratedAdventureValidationError(
                    "Progression trigger references a location without "
                    "enemies."
                )
            if location_key in defeated_locations:
                raise GeneratedAdventureValidationError(
                    "Progression cannot defeat the same location twice."
                )
            defeated_locations.add(location_key)

        if not _location_is_reachable(
            current_location,
            location_key,
            exits,
        ):
            raise GeneratedAdventureValidationError(
                "Progression trigger location is not reachable in order: "
                f"{location_title}"
            )
        current_location = location_key

    return spec
