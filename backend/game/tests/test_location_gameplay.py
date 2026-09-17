from types import SimpleNamespace
from unittest.mock import Mock

import pytest
from django.contrib.auth import get_user_model
from django.core.management import call_command

from accounts.models import PlayerCharacter
from chat.models import Room
from chat.services.room_participants_service import RoomParticipantsService
from game.core.action_processor import ActionProcessor
from game.core.game_command import GameCommand
from game.npc.npc_models import NPC
from game.services.game_start_service import GameStartService
from game.state.game_state_manager import GameStateManager
from game.state.runtime.models import Enemy as RuntimeEnemy
from world.models import Adventure, Choice, Enemy, Location
from world.seeders.world_seeder import WorldSeeder


@pytest.fixture
def location_game():
    user = get_user_model().objects.create_user(username="location-hero")
    character = PlayerCharacter.objects.create(user=user, name="Hero")
    adventure = Adventure.objects.create(title="Routes", creator=user)
    village = Location.objects.create(
        adventure=adventure, title="Village", description="A safe village", order=1
    )
    forest = Location.objects.create(
        adventure=adventure, title="Forest", description="Dark trees", order=2
    )
    distant = Location.objects.create(
        adventure=adventure, title="Distant", description="Far away", order=3
    )
    Choice.objects.create(
        location=village, next_location=forest, title="Forest path"
    )
    Choice.objects.create(
        location=forest, next_location=village, title="Village path"
    )
    Enemy.objects.create(adventure=adventure, name="goblin", hp=30, defense=0)
    room_record = Room.objects.create(
        name="location-room", owner=user, adventure=adventure
    )
    participant = RoomParticipantsService.add_human(room_record, user, character)
    state = GameStateManager()
    llm = Mock()
    llm.generate_world.return_value = {}
    llm.generate_intro.return_value = {"text": "Welcome"}
    notifier = Mock()
    GameStartService(WorldSeeder(state), llm, notifier, state).start_game(
        adventure.id, room_record.id, adventure=adventure
    )
    room = state.get_room(room_record.id)
    room.enemies["goblin"].location = str(village.id)
    room.enemies["wolf"] = RuntimeEnemy(
        id="wolf", name="wolf", hp=30, defense=0,
        attack_bonus=0, damage_die=6, damage_bonus=0,
        location=str(forest.id),
    )
    room.npcs["ranger"] = NPC(
        id="ranger", name="Ranger", dialog=["Welcome to the forest"],
        location=str(forest.id),
    )
    return state, room, participant.id, village, forest, distant, notifier


@pytest.mark.django_db
def test_start_and_inspect_use_current_location(location_game):
    state, room, participant_id, village, forest, _, notifier = location_game
    player = room.players[participant_id]
    assert player.location == str(village.id)
    started = notifier.emit.call_args.args[1]["payload"]
    assert started["game_state"]["players"][str(participant_id)]["location"] == str(village.id)
    assert ("move", str(forest.id)) in {
        (choice["action"], choice["target"]) for choice in started["choices"]
    }

    result = ActionProcessor(state).process(
        GameCommand(action="inspect"), room=room.name, participant_id=participant_id
    )
    assert result["result"]["location_name"] == "Village"
    assert result["result"]["description"] == "A safe village"
    assert result["result"]["enemies"] == ["goblin"]
    assert "wolf" not in result["result"]["enemies"]
    assert "ranger" not in {npc["id"] for npc in result["result"]["npcs"]}
    assert result["result"]["exits"] == [{"id": forest.id, "title": "Forest"}]


@pytest.mark.django_db
def test_talk_requires_npc_in_current_location_before_ai(location_game):
    state, room, participant_id, _, forest, _, _ = location_game
    dialogue = Mock(return_value="Ranger speaks")
    processor = ActionProcessor(state, dialogue_fn=dialogue)

    absent = processor.process(
        GameCommand(action="talk", target="ranger"),
        room=room.name, participant_id=participant_id,
    )
    assert absent["result"]["error"] == "npc_not_found"
    dialogue.assert_not_called()

    room.players[participant_id].location = str(forest.id)
    present = processor.process(
        GameCommand(action="talk", target="ranger"),
        room=room.name, participant_id=participant_id,
    )
    assert present["text"] == "Ranger speaks"
    assert present["result"]["npc"] == "Ranger"
    assert dialogue.call_args.args[2]["location"] == str(forest.id)


@pytest.mark.django_db
def test_move_validates_exit_then_changes_state_before_narration(location_game):
    state, room, participant_id, village, forest, distant, _ = location_game
    observed = []

    def narrate(action, result, world, details):
        observed.append((action, room.players[participant_id].location, result.copy()))
        return {"text": "The forest is ahead"}

    processor = ActionProcessor(state, narrate_fn=narrate)
    blocked = processor.process(
        GameCommand(action="move", target=str(distant.id)),
        room=room.name, participant_id=participant_id,
    )
    assert blocked["result"]["error"] == "invalid_exit"
    assert room.players[participant_id].location == str(village.id)
    assert room.player_histories[participant_id] == []
    assert observed == []

    moved = processor.process(
        GameCommand(action="move", target=str(forest.id)),
        room=room.name, participant_id=participant_id,
    )
    assert moved["result"]["location"] == str(forest.id)
    assert observed == [("move", str(forest.id), moved["result"])]
    assert ("attack", "wolf") in {
        (choice["action"], choice["target"]) for choice in moved["choices"]
    }
    assert ("talk", "ranger") in {
        (choice["action"], choice["target"]) for choice in moved["choices"]
    }
    assert ("move", str(village.id)) in {
        (choice["action"], choice["target"]) for choice in moved["choices"]
    }
    assert not any(choice["target"] == "goblin" for choice in moved["choices"])


@pytest.mark.django_db
def test_attack_only_reaches_living_enemy_in_current_location(location_game):
    state, room, participant_id, _, forest, _, _ = location_game
    room.players[participant_id].location = str(forest.id)
    observed = []

    def narrate(action, result, world, details):
        observed.append((room.enemies["wolf"].hp, result["attacker_damage"]))
        return {"text": "Attack narrated"}

    processor = ActionProcessor(state, narrate_fn=narrate)
    blocked = processor.process(
        GameCommand(action="attack", target="goblin"),
        room=room.name, participant_id=participant_id,
    )
    assert blocked["result"]["error"] == "enemy_not_found"
    assert room.player_histories[participant_id] == []
    assert observed == []

    attacked = processor.process(
        GameCommand(action="attack", target="wolf"),
        room=room.name, participant_id=participant_id,
    )
    assert attacked["result"]["attacker_damage"] > 0
    assert observed == [(room.enemies["wolf"].hp, attacked["result"]["attacker_damage"])]
    assert room.enemies["wolf"].hp == 30 - attacked["result"]["attacker_damage"]
    assert room.enemies["goblin"].hp == 30
    assert room.player_histories[participant_id][0]["action"] == "attack"


@pytest.mark.django_db
def test_canonical_start_inspect_talk_move_inspect_attack_loop(location_game):
    state, room, participant_id, village, forest, _, _ = location_game
    processor = ActionProcessor(state)

    def act(action, target=None):
        return processor.process(
            GameCommand(action=action, target=target),
            room=room.name, participant_id=participant_id,
        )

    first = act("inspect")
    assert first["result"]["location"] == str(village.id)
    assert act("talk", "old_man")["result"]["npc"] == "Old Man"
    assert act("move", str(forest.id))["result"]["location"] == str(forest.id)
    second = act("inspect")
    assert second["result"]["enemies"] == ["wolf"]
    assert "ranger" in {npc["id"] for npc in second["result"]["npcs"]}
    assert act("attack", "wolf")["result"]["attacker_damage"] > 0
    assert [entry["action"] for entry in room.player_histories[participant_id]] == [
        "inspect", "talk", "move", "inspect", "attack"
    ]
    assert room.current_player_id == participant_id


@pytest.mark.django_db
def test_seed_world_supports_vertical_slice_without_runtime_edits():
    user = get_user_model().objects.create_user(username="seeded-slice-hero")
    Adventure.objects.create(title="Unrelated adventure", creator=user)
    call_command("seed_world", verbosity=0)
    call_command("seed_world", verbosity=0)

    adventure = Adventure.objects.get(title="Przygoda startowa")
    village, forest, _ = list(adventure.locations.order_by("order", "id"))
    assert Choice.objects.filter(location=village, next_location=forest).exists()
    assert Choice.objects.filter(location=forest, next_location=village).exists()
    assert adventure.locations.count() == 3
    assert adventure.enemies.filter(name="goblin").count() == 1

    character = PlayerCharacter.objects.create(user=user, name="Seeded hero")
    room_record = Room.objects.create(
        name="seeded-slice-room", owner=user, adventure=adventure
    )
    participant = RoomParticipantsService.add_human(room_record, user, character)
    state = GameStateManager()
    llm = Mock()
    llm.generate_world.return_value = {}
    llm.generate_intro.return_value = {"text": "Welcome"}
    notifier = Mock()
    GameStartService(WorldSeeder(state), llm, notifier, state).start_game(
        adventure.id, room_record.id, adventure=adventure
    )
    runtime = state.get_room(room_record.id)
    started = notifier.emit.call_args.args[1]["payload"]
    assert runtime.players[participant.id].location == str(village.id)
    assert runtime.npcs["old_man"].location == str(village.id)
    assert runtime.npcs["merchant"].location == str(forest.id)
    assert runtime.enemies["goblin"].location == str(forest.id)
    assert ("move", str(forest.id)) in {
        (choice["action"], choice["target"]) for choice in started["choices"]
    }

    processor = ActionProcessor(state)

    def act(action, target=None):
        return processor.process(
            GameCommand(action=action, target=target),
            room=room_record.id, participant_id=participant.id,
        )

    first = act("inspect")
    assert first["result"]["location_name"] == village.title
    assert first["result"]["enemies"] == []
    assert act("talk", "old_man")["result"]["npc"] == "Old Man"
    assert act("move", str(forest.id))["result"]["location"] == str(forest.id)
    second = act("inspect")
    assert second["result"]["location_name"] == forest.title
    assert second["result"]["enemies"] == ["goblin"]
    assert act("attack", "goblin")["result"]["attacker_damage"] > 0
    assert runtime.enemies["goblin"].hp < 20


@pytest.mark.django_db
@pytest.mark.parametrize("location_count", [0, 1])
def test_seeded_entities_fall_back_to_start_for_small_adventures(location_count):
    user = get_user_model().objects.create_user(username=f"fallback-{location_count}")
    character = PlayerCharacter.objects.create(user=user, name="Hero")
    adventure = Adventure.objects.create(title="Small adventure", creator=user)
    if location_count:
        start = Location.objects.create(adventure=adventure, title="Only place")
    Enemy.objects.create(adventure=adventure, name="goblin")
    room_record = Room.objects.create(
        name="small-room", owner=user, adventure=adventure
    )
    participant = RoomParticipantsService.add_human(room_record, user, character)
    state = GameStateManager()
    llm = Mock()
    llm.generate_world.return_value = {}
    llm.generate_intro.return_value = {}
    GameStartService(WorldSeeder(state), llm, Mock(), state).start_game(
        adventure.id, room_record.id
    )

    runtime = state.get_room(room_record.id)
    expected = str(start.id) if location_count else "start"
    assert runtime.players[participant.id].location == expected
    assert runtime.enemies["goblin"].location == expected
    assert {npc.location for npc in runtime.npcs.values()} == {expected}


@pytest.mark.django_db
def test_cienie_eldorii_reference_adventure_completes_deterministically():
    user = get_user_model().objects.create_user(username="shadows-hero")
    character = PlayerCharacter.objects.create(user=user, name="Shadow hero")
    adventure = Adventure.objects.create(title="Cienie Eldorii", creator=user)
    village = Location.objects.create(
        adventure=adventure, title="Village", description="Village", order=1
    )
    forest = Location.objects.create(
        adventure=adventure, title="Forest", description="Forest", order=2
    )
    Choice.objects.create(location=village, next_location=forest, title="Forest")
    Choice.objects.create(location=forest, next_location=village, title="Village")
    Enemy.objects.create(adventure=adventure, name="goblin", hp=20, defense=0)
    room_record = Room.objects.create(name="shadows-room", owner=user, adventure=adventure)
    participant = RoomParticipantsService.add_human(room_record, user, character)
    state = GameStateManager()
    llm = Mock(generate_world=Mock(return_value={}), generate_intro=Mock(return_value={"text": ""}))
    GameStartService(WorldSeeder(state), llm, Mock(), state).start_game(
        adventure.id, room_record.id, adventure=adventure
    )
    room = state.get_room(room_record.id)
    processor = ActionProcessor(
        state,
        combat_service=SimpleNamespace(
            resolve=lambda attacker, defender: SimpleNamespace(
                attacker_damage=20, defender_damage=0
            )
        ),
    )

    def act(action, target=None):
        return processor.process(
            GameCommand(action=action, target=target),
            room=room_record.id, participant_id=participant.id,
        )

    assert room.quest.status == "not_started"
    failed = act("talk", "missing")
    assert failed["result"]["error"] == "npc_not_found"
    assert room.quest.status == "not_started"
    assert room.player_histories[participant.id] == []
    assert act("talk", "guard")["result"]["npc"] == "Guard"
    assert room.quest.status == "active"
    assert room.quest.flags["guard_spoken"] is True
    act("move", str(forest.id))
    act("attack", "goblin")
    assert room.quest.flags["enemy_defeated"] is True
    act("talk", "merchant")
    assert room.quest.flags["merchant_found"] is True
    act("move", str(village.id))

    snapshot = state.build_game_state(room)
    assert snapshot["quest"]["status"] == "completed"
    assert snapshot["quest"]["completed"] is True
    assert snapshot["adventure_completed"] is True
    assert snapshot["npcs"]["guard"]["location"] == str(village.id)
    assert snapshot["enemies"]["goblin"]["hp"] == 0


@pytest.mark.django_db
def test_cienie_eldorii_cannot_skip_required_progression_order():
    user = get_user_model().objects.create_user(username="shadows-order-hero")
    character = PlayerCharacter.objects.create(user=user, name="Order hero")
    call_command("seed_world", verbosity=0)
    adventure = Adventure.objects.get(title="Cienie Eldorii")
    village = adventure.locations.get(title="Village")
    forest = adventure.locations.get(title="Forest")
    room_record = Room.objects.create(name="shadows-order-room", owner=user, adventure=adventure)
    participant = RoomParticipantsService.add_human(room_record, user, character)
    state = GameStateManager()
    llm = Mock(generate_world=Mock(return_value={}), generate_intro=Mock(return_value={"text": ""}))
    GameStartService(WorldSeeder(state), llm, Mock(), state).start_game(
        adventure.id, room_record.id, adventure=adventure
    )
    room = state.get_room(room_record.id)
    processor = ActionProcessor(state)

    def act(action, target=None):
        return processor.process(
            GameCommand(action=action, target=target),
            room=room_record.id, participant_id=participant.id,
        )

    act("talk", "guard")
    act("move", str(forest.id))
    act("move", str(village.id))
    assert room.quest.completed is False
    assert room.adventure_completed is False

    act("move", str(forest.id))
    act("talk", "merchant")
    assert room.quest.flags.get("merchant_found") is not True
    act("move", str(village.id))
    assert room.quest.completed is False
    assert room.adventure_completed is False
