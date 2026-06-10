import pytest
from django.db import connection
from django.contrib.auth import get_user_model


@pytest.fixture(autouse=True)
def _django_db_all_access(db):
    pass

@pytest.fixture
def user(db):
    User = get_user_model()
    return User.objects.create_user(
        username="testuser",
        email="test@example.com",
        password="testpass"
    )


@pytest.fixture
def another_user(db):
    User = get_user_model()
    return User.objects.create_user(
        username="otheruser",
        email="other@example.com",
        password="testpass"
    )