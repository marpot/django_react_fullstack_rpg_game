from game.state.game_state_manager import Enemy, GameStateManager, NPC, QuestState
from game.state.runtime.models import Player


def test_new_room_has_default_quest_and_adventure_progression_state():
    state = GameStateManager()

    room = state.get_or_create_room("quest-defaults")

    assert room.quest == QuestState()
    assert room.quest.status == "not_started"
    assert room.quest.stage is None
    assert room.quest.objective is None
    assert room.quest.flags == {}
    assert room.quest.completed is False
    assert room.adventure_completed is False


def test_build_game_state_contains_quest_npcs_and_completion():
    state = GameStateManager()
    room = state.get_or_create_room("snapshot")
    room.npcs["guard"] = NPC(id="guard", name="Guard", state="idle")
    room.quest.status = "active"
    room.quest.stage = "village"
    room.quest.objective = "Find the guard"
    room.quest.flags["met_guard"] = True
    room.adventure_completed = True

    snapshot = state.build_game_state(room)

    assert snapshot["quest"] == {
        "status": "active",
        "stage": "village",
        "objective": "Find the guard",
        "flags": {"met_guard": True},
        "completed": False,
    }
    assert snapshot["npcs"]["guard"]["id"] == "guard"
    assert snapshot["npcs"]["guard"]["name"] == "Guard"
    assert snapshot["adventure_completed"] is True


def test_quest_changes_are_visible_in_next_snapshot():
    state = GameStateManager()
    room = state.get_or_create_room("progression")

    first = state.build_game_state(room)
    room.quest.status = "completed"
    room.quest.stage = "return"
    room.quest.objective = "Return to the village"
    room.quest.completed = True

    second = state.build_game_state(room)

    assert first["quest"]["status"] == "not_started"
    assert second["quest"]["status"] == "completed"
    assert second["quest"]["stage"] == "return"
    assert second["quest"]["completed"] is True


def test_room_runtime_state_is_isolated_between_rooms():
    state = GameStateManager()
    first_room = state.get_or_create_room("first")
    second_room = state.get_or_create_room("second")
    first_room.quest.status = "active"
    first_room.quest.flags["started"] = True
    first_room.npcs["guard"] = NPC(id="guard", name="Guard")
    first_room.adventure_completed = True

    second_snapshot = state.build_game_state(second_room)

    assert second_snapshot["quest"]["status"] == "not_started"
    assert second_snapshot["quest"]["flags"] == {}
    assert second_snapshot["npcs"] == {}
    assert second_snapshot["adventure_completed"] is False


def test_build_game_state_preserves_existing_players_enemies_and_histories():
    state = GameStateManager()
    room = state.get_or_create_room("existing-state")
    room.players[7] = Player(
        id=7,
        name="Hero",
        hp=12,
        max_hp=20,
        attack_bonus=3,
        damage_die=6,
        damage_bonus=1,
        defense=2,
    )
    room.enemies["wolf"] = Enemy(
        name="wolf",
        hp=8,
        defense=11,
        attack_bonus=2,
        damage_die=6,
        damage_bonus=0,
    )
    room.player_histories[7] = [{"action": "inspect"}]

    snapshot = state.build_game_state(room)

    assert snapshot["players"]["7"]["hp"] == 12
    assert snapshot["enemies"]["wolf"]["hp"] == 8
    assert snapshot["player_histories"]["7"] == [{"action": "inspect"}]
