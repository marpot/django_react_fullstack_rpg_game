from game.core.action_processor import ActionProcessor
from game.state.game_state_manager import GameStateManager
from game.state.runtime.models import Player, Enemy


def test_attack_action():
    state = GameStateManager()
    room = state.get_or_create_room("testroom")

    state.add_player(
        "testroom",
        1,
        Player(
            id=1,
            name="Hero",
            hp=100,
            max_hp=100,
            attack_bonus=10,
            damage_die=8,
            damage_bonus=2,
            defense=5,
        )
    )

    
    state.add_enemy(
        "testroom",
        Enemy(
              id="goblin", 
              name="goblin", 
              hp=10,
              defense=2,
              attack_bonus=1,
              damage_die=6,
              damage_bonus=1
            )
    )

    processor = ActionProcessor(state)

    parsed = {
        "action": "attack",
        "target": "goblin",
        "room": "testroom",
        "user_id": 1
    }

    result = processor.process(parsed)

    assert "action" in result
    assert result["action"] == "attack"

    assert room.enemies["goblin"].hp < 10