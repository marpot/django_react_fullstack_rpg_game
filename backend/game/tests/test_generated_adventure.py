import pytest

from game.domain.generated_adventure import (
    GeneratedAdventureSpec,
    GeneratedAdventureValidationError,
    GeneratedChoiceSpec,
    GeneratedEnemySpec,
    GeneratedLocationSpec,
    GeneratedNPCSpec,
    GeneratedProgressionStep,
    validate_generated_adventure,
)


def build_valid_spec() -> GeneratedAdventureSpec:
    return GeneratedAdventureSpec(
        title="Próba Eldorii",
        description="Mała przygoda testowa.",
        start_location="village",
        locations=(
            GeneratedLocationSpec(
                key="village",
                title="Wioska",
                description="Spokojna wioska.",
            ),
            GeneratedLocationSpec(
                key="forest",
                title="Las",
                description="Niebezpieczny las.",
            ),
        ),
        choices=(
            GeneratedChoiceSpec(
                title="Idź do lasu",
                description="Droga prowadzi do lasu.",
                from_location="village",
                to_location="forest",
            ),
        ),
        enemies=(
            GeneratedEnemySpec(
                key="goblin",
                name="Goblin",
                location="forest",
            ),
        ),
        npcs=(
            GeneratedNPCSpec(
                key="guard",
                name="Strażnik",
                role="Strażnik wioski",
                location="village",
            ),
        ),
        progression=(
            GeneratedProgressionStep(
                stage="forest",
                trigger="talk:guard@village",
                objective="Idź do lasu.",
                next_stage="completed",
            ),
            GeneratedProgressionStep(
                stage="completed",
                trigger="defeat:enemy@forest",
                objective="",
                next_stage=None,
            ),
        ),
    )


def test_valid_generated_adventure_is_accepted():
    spec = build_valid_spec()

    assert validate_generated_adventure(spec) is spec


def test_unknown_start_location_is_rejected():
    spec = build_valid_spec()

    invalid = GeneratedAdventureSpec(
        **{
            **spec.__dict__,
            "start_location": "unknown",
        }
    )

    with pytest.raises(
        GeneratedAdventureValidationError,
        match="Start location",
    ):
        validate_generated_adventure(invalid)


def test_choice_with_unknown_location_is_rejected():
    spec = build_valid_spec()

    invalid_choice = GeneratedChoiceSpec(
        title="Zniknij",
        description="Niepoprawne przejście.",
        from_location="village",
        to_location="void",
    )

    invalid = GeneratedAdventureSpec(
        **{
            **spec.__dict__,
            "choices": (invalid_choice,),
        }
    )

    with pytest.raises(
        GeneratedAdventureValidationError,
        match="unknown target location",
    ):
        validate_generated_adventure(invalid)


def test_enemy_with_unknown_location_is_rejected():
    spec = build_valid_spec()

    invalid_enemy = GeneratedEnemySpec(
        key="goblin",
        name="Goblin",
        location="void",
    )

    invalid = GeneratedAdventureSpec(
        **{
            **spec.__dict__,
            "enemies": (invalid_enemy,),
        }
    )

    with pytest.raises(
        GeneratedAdventureValidationError,
        match="Enemy references unknown location",
    ):
        validate_generated_adventure(invalid)


def test_npc_with_unknown_location_is_rejected():
    spec = build_valid_spec()

    invalid_npc = GeneratedNPCSpec(
        key="guard",
        name="Strażnik",
        role="Strażnik",
        location="void",
    )

    invalid = GeneratedAdventureSpec(
        **{
            **spec.__dict__,
            "npcs": (invalid_npc,),
        }
    )

    with pytest.raises(
        GeneratedAdventureValidationError,
        match="NPC references unknown location",
    ):
        validate_generated_adventure(invalid)


def test_progression_with_unknown_next_stage_is_rejected():
    spec = build_valid_spec()

    invalid_step = GeneratedProgressionStep(
        stage="forest",
        trigger="talk:guard@village",
        objective="Idź do lasu.",
        next_stage="missing",
    )

    invalid = GeneratedAdventureSpec(
        **{
            **spec.__dict__,
            "progression": (invalid_step,),
        }
    )

    with pytest.raises(
        GeneratedAdventureValidationError,
        match="unknown next stage",
    ):
        validate_generated_adventure(invalid)
