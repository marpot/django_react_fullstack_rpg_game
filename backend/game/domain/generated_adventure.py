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

        if npc.location not in known_locations:
            raise GeneratedAdventureValidationError(
                f"NPC references unknown location: {npc.location}"
            )

    stages = [step.stage for step in spec.progression]

    if len(stages) != len(set(stages)):
        raise GeneratedAdventureValidationError(
            "Progression stages must be unique."
        )

    known_stages = set(stages)

    for step in spec.progression:
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

    return spec
