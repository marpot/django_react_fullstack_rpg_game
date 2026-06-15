import pytest
from rest_framework.test import APIClient
from django.contrib.auth import get_user_model

from accounts.models import PlayerCharacter
from world.models import Adventure
from game.models import GameSession

pytestmark = pytest.mark.django_db


def test_npcs_endpoint():
    client = APIClient()

    User = get_user_model()

    user = User.objects.create_user(
        username="hero",
        password="test123"
    )

    player = PlayerCharacter.objects.create(
        user=user,
        name="Hero"
    )

    adventure = Adventure.objects.create(
        title="Test World",
        creator=user   # 🔥 FIX
    )

    session = GameSession.objects.create(
        player=player,
        progress={
            "adventure_id": adventure.id
    }
)

    response = client.get(f"/api/game/sessions/{session.id}/npcs/")

    assert response.status_code == 200
    assert "npcs" in response.data