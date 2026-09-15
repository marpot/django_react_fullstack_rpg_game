import pytest
from rest_framework.test import APIClient

from accounts.models import PlayerCharacter
from chat.models import Room, RoomParticipant


pytestmark = pytest.mark.django_db


def _select_character(client, room, character):
    return client.post(
        f"/api/chat/rooms/{room.id}/select_character/",
        {"character_id": character.id},
        format="json",
    )


def test_user_can_select_own_character(user):
    room = Room.objects.create(name="own-character", owner=user)
    character = PlayerCharacter.objects.create(user=user, name="Hero")
    client = APIClient()
    client.force_authenticate(user=user)

    response = _select_character(client, room, character)

    assert response.status_code == 200
    participant = RoomParticipant.objects.get(room=room, user=user)
    assert response.data == {
        "participant_id": participant.id,
        "character_id": character.id,
        "name": character.name,
        "is_ai": False,
        "is_current_user": True,
    }


def test_user_cannot_select_another_users_character(user, another_user):
    room = Room.objects.create(name="foreign-character", owner=user)
    character = PlayerCharacter.objects.create(
        user=another_user,
        name="Not yours",
    )
    client = APIClient()
    client.force_authenticate(user=user)

    response = _select_character(client, room, character)

    assert response.status_code == 404
    assert not RoomParticipant.objects.filter(room=room, user=user).exists()


def test_reselect_updates_participant_without_duplicate(user):
    room = Room.objects.create(name="reselect-character", owner=user)
    first = PlayerCharacter.objects.create(user=user, name="First")
    second = PlayerCharacter.objects.create(user=user, name="Second")
    client = APIClient()
    client.force_authenticate(user=user)

    first_response = _select_character(client, room, first)
    second_response = _select_character(client, room, second)

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

    client.force_authenticate(user=user)
    first_response = _select_character(client, room, first)
    client.force_authenticate(user=another_user)
    second_response = _select_character(client, room, second)

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
