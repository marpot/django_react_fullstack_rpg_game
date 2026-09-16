from unittest.mock import Mock

import pytest
from django.contrib.auth import get_user_model

from accounts.models import PlayerCharacter
from chat.models import Room
from chat.services.room_participants_service import RoomParticipantsService
from game.core.action_processor import ActionProcessor
from game.core.game_command import GameCommand
from game.services.game_start_service import GameStartService
from game.state.game_state_manager import GameStateManager
from game_instances.services.llm.orchestrator.llm_service import LLMService
from world.models import Adventure, Enemy
from world.seeders.world_seeder import WorldSeeder


@pytest.mark.django_db
def test_two_players_start_act_and_advance_canonical_turn(fake_llm_provider):
    for index in range(3):
        padding_user = get_user_model().objects.create_user(
            username=f"slice-padding-{index}", password="x"
        )
        PlayerCharacter.objects.create(user=padding_user, name=f"Padding {index}")

    users = [
        get_user_model().objects.create_user(username=f"slice-{index}", password="x")
        for index in range(2)
    ]
    characters = [
        PlayerCharacter.objects.create(user=user, name=f"Hero {index}")
        for index, user in enumerate(users)
    ]
    adventure = Adventure.objects.create(
        title="Slice adventure", description="A small adventure", creator=users[0]
    )
    Enemy.objects.create(adventure=adventure, name="Goblin")
    room = Room.objects.create(name="slice-room", owner=users[0], adventure=adventure)
    participants = [
        RoomParticipantsService.add_human(room, user, character)
        for user, character in zip(users, characters)
    ]

    state = GameStateManager()
    notifier = Mock()
    world = GameStartService(
        seeder=WorldSeeder(state),
        llm=LLMService(),
        notifier=notifier,
        state_manager=state,
    ).start_game(adventure.id, room.id, adventure=adventure)

    runtime = state.get_room(room.id)
    participant_ids = [participant.id for participant in participants]
    assert set(participant_ids).isdisjoint({user.id for user in users})
    assert set(participant_ids).isdisjoint({character.id for character in characters})
    assert runtime.started is True
    assert runtime.world == world
    assert runtime.turn_order == participant_ids
    assert runtime.current_player_id == participants[0].id
    assert set(runtime.players) == set(participant_ids)
    for user, character, participant in zip(users, characters, participants):
        player = runtime.players[participant.id]
        assert (player.id, player.user_id, player.character_id) == (
            participant.id, user.id, character.id
        )
    assert "goblin" in runtime.enemies
    notifier.emit.assert_called_once()

    processor = ActionProcessor(state)
    result = processor.process(
        GameCommand(action="inspect", target=None, method=None),
        room=room.id,
        participant_id=participants[0].id,
        adventure=adventure.id,
        world=world,
    )

    assert result["action"] == "inspect"
    assert result["result"]["room"] == str(room.id)
    assert result["text"] == "Narracja testowa."
    assert runtime.player_histories[participants[0].id][0]["action"] == "inspect"
    assert runtime.player_histories[participants[1].id] == []
    assert runtime.current_player_id == participants[1].id
    assert runtime.current_turn_index == 1
    assert result["turn_state"]["current_player_id"] == participants[1].id

    rejected = processor.process(
        GameCommand(action="inspect"),
        room=room.id,
        participant_id=participants[0].id,
        adventure=adventure.id,
        world=world,
    )
    assert rejected["result"]["error"] == "not_your_turn"
    assert runtime.current_player_id == participants[1].id
    assert len(runtime.player_histories[participants[0].id]) == 1
    assert runtime.player_histories[participants[1].id] == []
