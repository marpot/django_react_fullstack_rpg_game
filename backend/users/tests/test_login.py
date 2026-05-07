import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

@pytest.mark.django_db
def test_user_login():
    user = get_user_model().objects.create_user(
        username="testuser",
        email="testuser@example.com",
        password="testpassword123"
    )

    client = APIClient()

    response = client.post(reverse("login"), {
        "username": "testuser",
        "password": "testpassword123"
    }, format="json")

    assert response.status_code == status.HTTP_200_OK
    assert "access" in response.data

@pytest.mark.django_db
def test_user_login_invalid_credentials():
    client = APIClient()

    response = client.post(reverse("login"), {
        "username": "wronguser",
        "password": "wrongpassword"
    }, format="json")

    assert response.status_code == status.HTTP_400_BAD_REQUEST
    assert "non_field_errors" in response.data
    assert any("Invalid credentials" in msg for msg in response.data["non_field_errors"])