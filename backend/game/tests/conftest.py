import pytest
from game_instances.services.llm.core import llm_client
from world.models import Adventure
from users.models import CustomUser
from world.models import Location


class FakeLLMProvider:
    def __init__(self):
        self.error = None

    def complete(self, system_prompt, user_prompt):
        if self.error is not None:
            raise self.error
        return "Narracja testowa."


@pytest.fixture
def fake_llm_provider(monkeypatch):
    provider = FakeLLMProvider()
    monkeypatch.setattr(llm_client, "GroqProvider", lambda config=None: provider)
    return provider

@pytest.fixture
def test_adventure(db, test_user):
    return Adventure.objects.create(
        title="Testowa przygoda",
        description="To jest testowa przygoda",
        creator=test_user,
    )

@pytest.fixture
def test_user():
    return CustomUser.objects.create_user(
        username="testuser",
        password="testpassword",
    )

@pytest.fixture
def test_location(db):
    return Location.objects.create(
        title="Test Location",
        description="Test Description"
    )
