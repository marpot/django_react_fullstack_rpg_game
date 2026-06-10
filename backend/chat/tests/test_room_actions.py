import pytest
from rest_framework.test import APIClient
from chat.models import Room
from world.models import Adventure


@pytest.mark.django_db
def test_set_adventure_only_owner_can_do_it(user, another_user):
    client = APIClient()

    adventure = Adventure.objects.create(
        title="Test",
        description="Test",
        creator=user
    )

    room = Room.objects.create(owner=user, state="lobby")

    client.force_authenticate(user=another_user)

    response = client.post(
        f"/api/chat/rooms/{room.id}/set_adventure/",
        {"adventure_id": adventure.id},
        format="json"
    )

    assert response.status_code in (400, 403)


@pytest.mark.django_db
def test_set_adventure_success(user):
    client = APIClient()

    adventure = Adventure.objects.create(
        title="Test",
        description="Test",
        creator=user
    )

    room = Room.objects.create(owner=user, state="lobby")

    client.force_authenticate(user=user)

    response = client.post(
        f"/api/chat/rooms/{room.id}/set_adventure/",
        {"adventure_id": adventure.id},
        format="json"
    )

    assert response.status_code == 200
    assert response.data["adventure_id"] == adventure.id