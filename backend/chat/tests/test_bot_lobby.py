import pytest
from rest_framework.test import APIClient

from chat.models import Room, RoomParticipant


pytestmark = pytest.mark.django_db


def client_for(user):
    client = APIClient()
    client.force_authenticate(user=user)
    return client


def test_owner_can_add_one_ai_and_repeat_is_idempotent(user):
    room = Room.objects.create(name="bot-lobby", owner=user)
    client = client_for(user)

    first = client.post(f"/api/chat/rooms/{room.id}/add_ai/")
    second = client.post(f"/api/chat/rooms/{room.id}/add_ai/")

    assert first.status_code == second.status_code == 200
    assert first.data["is_ai"] is True
    assert second.data["participant_id"] == first.data["participant_id"]
    assert RoomParticipant.objects.filter(room=room, is_ai=True).count() == 1


def test_owner_can_remove_ai(user):
    room = Room.objects.create(name="remove-bot-lobby", owner=user)
    client = client_for(user)
    client.post(f"/api/chat/rooms/{room.id}/add_ai/")

    response = client.post(f"/api/chat/rooms/{room.id}/remove_ai/")

    assert response.status_code == 200
    assert response.data == {"removed": True}
    assert not RoomParticipant.objects.filter(room=room, is_ai=True).exists()


def test_non_owner_cannot_manage_ai(user, another_user):
    room = Room.objects.create(name="protected-bot-lobby", owner=user)
    client = client_for(another_user)

    add_response = client.post(f"/api/chat/rooms/{room.id}/add_ai/")
    remove_response = client.post(f"/api/chat/rooms/{room.id}/remove_ai/")

    assert add_response.status_code == remove_response.status_code == 403
    assert not RoomParticipant.objects.filter(room=room, is_ai=True).exists()


@pytest.mark.parametrize("action", ["add_ai", "remove_ai"])
def test_ai_cannot_change_after_game_started(user, action):
    room = Room.objects.create(name="started-bot-room", owner=user, state="in_game")
    client = client_for(user)

    response = client.post(f"/api/chat/rooms/{room.id}/{action}/")

    assert response.status_code == 400
    assert response.data["code"] == "ROOM_NOT_IN_LOBBY"
