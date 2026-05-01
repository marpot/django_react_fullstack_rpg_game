import pytest
from world.models import Adventure
from users.models import CustomUser
from world.models import Location

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