from game.state.game_state_manager import GameStateManager
from game.core.action_processor import ActionProcessor
from game.state.runtime.models import Player, Enemy

def test_full_combat_flow():
    state = GameStateManager()
    processor = ActionProcessor(state)

    room = state.get_or_create_room("testroom")

    state.add_player(
        "testroom",
        1,
        Player(
            id = 1,
            name = "Hero",
            hp = 100,
            max_hp= 100,
            attack_bonus= 10,
            damage_die= 8,
            damage_bonus= 2,
            defense= 5
        )
    )

    room.enemies['goblin'] = Enemy(
        id = "goblin",
        name="goblin",
        hp=30,
        defense=2,
        attack_bonus=1,
        damage_die=6,
        damage_bonus=1
    )

    result = processor.process({
        "action": "attack",
        "target": "goblin",
        "room": "testroom",
        "user_id": 1
    })

    assert result["action"] == "attack"
    assert result["result"] is not None
    assert room.enemies["goblin"].hp < 30