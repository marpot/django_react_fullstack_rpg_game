from game.core.action_processor import ActionProcessor
from game.core.choice_service import AdventureChoiceService
from game.core.game_command import ALLOWED_ACTIONS, GameCommand
from game.services.combat_service import CombatService
from game.services.dice_service import DiceService
from game.state.game_state_manager import GameStateManager, NPC
from game.state.runtime.models import Enemy, Player


def test_choices_follow_current_room_state_and_are_bounded():
    room = GameStateManager().get_or_create_room("choices")
    goblin = room.enemies["goblin"]
    room.enemies["Goblin"] = goblin  # WorldSeeder may expose two keys for one enemy.
    room.npcs["guide"] = NPC(id="guide", name="Guide")
    service = AdventureChoiceService()

    choices = service.build_choices(enemies=room.enemies, npcs=room.npcs)
    assert choices[0]["action"] == "inspect"
    assert [(choice["action"], choice["target"]) for choice in choices].count(
        ("attack", "goblin")
    ) == 1
    assert ("talk", "guide") in [
        (choice["action"], choice["target"]) for choice in choices
    ]
    assert all(choice["action"] in ALLOWED_ACTIONS for choice in choices)
    assert all(GameCommand.from_mapping(choice).method is None for choice in choices)
    assert all("move" != choice["action"] for choice in choices)

    goblin.hp = 0
    updated = service.build_choices(enemies=room.enemies, npcs=room.npcs)
    assert not any(choice["action"] == "attack" for choice in updated)
    assert any(choice["action"] == "inspect" for choice in updated)

    for index in range(20):
        room.enemies[f"enemy-{index}"] = Enemy(
            id=f"enemy-{index}", name=f"enemy-{index}", hp=10,
            defense=10, attack_bonus=0, damage_die=6, damage_bonus=0,
        )
    room.npcs["merchant"] = NPC(id="merchant", name="Merchant")
    limited = service.build_choices(enemies=room.enemies, npcs=room.npcs)
    assert len(limited) <= service.MAX_CHOICES
    assert any(choice["action"] == "talk" for choice in limited)


def test_attack_result_choices_exclude_enemy_killed_by_that_attack(fake_llm_provider):
    state = GameStateManager()
    room = state.get_or_create_room("choice-after-attack")
    room.players[1] = Player(
        id=1, name="Hero", hp=100, max_hp=100, attack_bonus=10,
        damage_die=6, damage_bonus=0, defense=10,
    )
    room.enemies["goblin"].hp = 1
    room.enemies["goblin"].defense = 0
    room.turn_order = [1]
    room.current_player_id = 1
    room.player_histories = {1: []}

    result = ActionProcessor(
        state, combat_service=CombatService(DiceService(seed=1))
    ).process(
        GameCommand(action="attack", target="goblin"),
        room=room.name,
        participant_id=1,
    )

    assert result["action"] == "attack"
    assert room.enemies["goblin"].hp == 0
    assert not any(choice["action"] == "attack" for choice in result["choices"])
    assert any(choice["action"] == "inspect" for choice in result["choices"])
