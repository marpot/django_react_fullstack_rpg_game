import pytest
from rest_framework.test import APIClient

from accounts.models import PlayerCharacter
from chat.models import Room, RoomParticipant
from world.models import Adventure


pytestmark = pytest.mark.django_db


def _join_room(client, room):
    return client.post(
        f"/api/chat/rooms/{room.id}/join/",
        {},
        format="json",
    )


def test_join_assigns_users_active_character(user):
    room = Room.objects.create(name="own-character", owner=user)
    character = PlayerCharacter.objects.create(user=user, name="Hero")
    client = APIClient()
    client.force_authenticate(user=user)

    select_response = client.post(
        "/api/accounts/select-active-character/",
        {"character_id": character.id},
        format="json",
    )

    response = _join_room(client, room)

    assert select_response.status_code == 200
    assert response.status_code == 200
    participant = RoomParticipant.objects.get(room=room, user=user)
    assert response.data == {
        "participant_id": participant.id,
        "character_id": character.id,
        "name": character.name,
        "is_ai": False,
        "is_current_user": True,
    }


def test_join_does_not_assign_another_users_active_character(user, another_user):
    room = Room.objects.create(name="foreign-character", owner=user)
    character = PlayerCharacter.objects.create(
        user=another_user,
        name="Not yours",
    )
    client = APIClient()
    client.force_authenticate(user=user)

    select_response = client.post(
        "/api/accounts/select-active-character/",
        {"character_id": character.id},
        format="json",
    )

    response = _join_room(client, room)

    assert select_response.status_code == 404
    assert response.status_code == 400
    assert response.data["code"] == "NO_ACTIVE_CHARACTER"
    assert not RoomParticipant.objects.filter(room=room, user=user).exists()


def test_join_without_active_character_returns_controlled_error(user):
    room = Room.objects.create(name="no-active-character", owner=user)
    client = APIClient()
    client.force_authenticate(user=user)

    response = _join_room(client, room)

    assert response.status_code == 400
    assert response.data == {
        "code": "NO_ACTIVE_CHARACTER",
        "error": "Select an active character in Profile first.",
    }
    assert not RoomParticipant.objects.filter(room=room, user=user).exists()


def test_rejoin_updates_participant_after_profile_selection_without_duplicate(user):
    room = Room.objects.create(name="reselect-character", owner=user)
    first = PlayerCharacter.objects.create(user=user, name="First")
    second = PlayerCharacter.objects.create(user=user, name="Second")
    client = APIClient()
    client.force_authenticate(user=user)

    select_first_response = client.post(
        "/api/accounts/select-active-character/",
        {"character_id": first.id},
        format="json",
    )
    first_response = _join_room(client, room)

    select_second_response = client.post(
        "/api/accounts/select-active-character/",
        {"character_id": second.id},
        format="json",
    )
    second_response = _join_room(client, room)

    assert select_first_response.status_code == 200
    assert select_second_response.status_code == 200
    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert first_response.data["participant_id"] == second_response.data["participant_id"]
    assert RoomParticipant.objects.filter(room=room, user=user).count() == 1
    participant = RoomParticipant.objects.get(room=room, user=user)
    assert participant.character == second
    assert participant.name == second.name
    assert participant.is_ai is False


def test_two_users_can_select_characters_in_same_room(user, another_user):
    room = Room.objects.create(name="two-users", owner=user)
    first = PlayerCharacter.objects.create(user=user, name="First")
    second = PlayerCharacter.objects.create(user=another_user, name="Second")
    client = APIClient()

    first.is_active = True
    first.save(update_fields=["is_active"])
    second.is_active = True
    second.save(update_fields=["is_active"])

    client.force_authenticate(user=user)
    first_response = _join_room(client, room)
    client.force_authenticate(user=another_user)
    second_response = _join_room(client, room)

    assert first_response.status_code == 200
    assert second_response.status_code == 200
    assert RoomParticipant.objects.filter(room=room).count() == 2
    assert set(
        RoomParticipant.objects.filter(room=room).values_list(
            "character_id",
            flat=True,
        )
    ) == {first.id, second.id}


def test_room_detail_lists_participants_without_user_data(user, another_user):
    room = Room.objects.create(name="participant-list", owner=user)
    first = PlayerCharacter.objects.create(user=user, name="First")
    second = PlayerCharacter.objects.create(user=another_user, name="Second")
    RoomParticipant.objects.create(
        room=room,
        user=user,
        character=first,
        name=first.name,
    )
    RoomParticipant.objects.create(
        room=room,
        user=another_user,
        character=second,
        name=second.name,
    )
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.get(f"/api/chat/rooms/{room.id}/")

    assert response.status_code == 200
    assert len(response.data["participants"]) == 2
    assert sum(
        participant["is_current_user"]
        for participant in response.data["participants"]
    ) == 1
    assert all(
        "user" not in participant and "user_id" not in participant
        for participant in response.data["participants"]
    )


def test_room_detail_returns_empty_participants_list(user):
    room = Room.objects.create(name="empty-participant-list", owner=user)
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.get(f"/api/chat/rooms/{room.id}/")

    assert response.status_code == 200
    assert response.data["participants"] == []


def test_room_detail_returns_owner_and_adventure_contract(user):
    adventure = Adventure.objects.create(title="Lobby adventure", creator=user)
    room = Room.objects.create(
        name="room-contract",
        owner=user,
        adventure=adventure,
    )
    client = APIClient()
    client.force_authenticate(user=user)

    response = client.get(f"/api/chat/rooms/{room.id}/")

    assert response.status_code == 200
    assert response.data["owner"] == user.id
    assert response.data["owner_id"] == user.id
    assert response.data["adventure"] == adventure.id
