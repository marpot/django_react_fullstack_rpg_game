from types import SimpleNamespace
from unittest.mock import Mock

from game.core.actions.action_talk import TalkAction


def test_talk_action_uses_resolved_npc_for_dialogue_and_progression_metadata():
    player = SimpleNamespace(name="Hero", location="village")
    room = SimpleNamespace(
        players={7: player},
        player_histories={7: [{"action": "inspect"}]},
    )
    state_manager = Mock()
    state_manager.normalize_room_id.return_value = "room-7"
    state_manager.get_or_create_room.return_value = room

    response_fn = Mock(
        return_value={
            "action": "talk",
            "text": "AI response",
            "result": {"npc": "Guide"},
        }
    )
    dialogue_fn = Mock(return_value="AI response")
    action = TalkAction(state_manager, dialogue_fn, response_fn)
    action.npc_service.talk = Mock(
        return_value={
            "action": "talk",
            "npc": "Guide",
            "npc_id": "guide",
            "personality": "wise",
            "text": "Original response",
        }
    )

    result = action.handle(
        {"room": "room-7", "participant_id": 7, "target": "guide"},
        {"title": "Crypt"},
        player_message="Porozmawiaj z przewodnikiem",
    )

    action.npc_service.talk.assert_called_once_with(
        "room-7", "guide", location="village"
    )
    canonical, world, details = dialogue_fn.call_args.args
    assert canonical["npc_id"] == "guide"
    assert canonical["personality"] == "wise"
    assert world == {"title": "Crypt"}
    assert details == {
        "actor": "Hero",
        "location": "village",
        "player_message": "Porozmawiaj z przewodnikiem",
        "recent_actions": ["inspect"],
    }

    response_result = response_fn.call_args.args[2]
    assert "npc_id" not in response_result
    assert "personality" not in response_result
    assert result["_progression_npc_id"] == "guide"
