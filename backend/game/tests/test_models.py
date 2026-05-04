import pytest
from users.models import CustomUser
from accounts.models import PlayerCharacter
from game.models import GameEvent, GameSession
from game.tests.conftest import test_adventure, test_user

@pytest.fixture
def test_player_character(db, test_user, test_adventure, test_location):  
    return PlayerCharacter.objects.create(
        user=test_user,
        name="Testowa_postac",
        current_location=test_location,
        adventure=test_adventure,
        stats = {"strength": 10, "agility": 8}
    )

@pytest.fixture
def test_game_event(db, test_player_character, test_adventure):
    return GameEvent.objects.create(
        player=test_player_character,
        location=None,
        description="Test description",
        timestamp="2023-05-01 12:00:00",
        adventure=test_adventure,  # Ustaw wartość w kolumnie adventure_id
    )

@pytest.fixture
def test_game_session(db, test_player_character):
    return GameSession.objects.create(
        player=test_player_character,
        progress={"level": 1},
        )

def test_game_session_creation(test_game_session):
    assert test_game_session.created_at is not None
    assert test_game_session.updated_at is not None
    assert test_game_session.created_at <= test_game_session.updated_at

def test_game_event_creation(test_game_event):
    assert test_game_event.player == test_player_character
    assert test_game_event.location is None
    assert test_game_event.description == "Test description"
    assert test_game_event.timestamp == "2023-05-01 12:00:00"

def test_game_event_creation(test_game_event):
    assert GameEvent.objects.count() == 1
    assert GameEvent.objects.get(id=test_game_event.id) == test_game_event