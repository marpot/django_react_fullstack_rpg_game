import pytest
from django.contrib.auth import get_user_model
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

@pytest.mark.django_db
def test_user_login():
    # Tworzymy użytkownika
    user = get_user_model().objects.create_user(
        username='testuser',
        email='testuser@example.com',
        password='testpassword123'
    )

    client = APIClient()
    data = {
        'username': 'testuser',
        'password': 'testpassword123'
    }

    # Wysłanie żądania logowania
    response = client.post(reverse('login'), data, format='json')

    # Sprawdzamy status odpowiedzi oraz czy token jest obecny
    assert response.status_code == status.HTTP_200_OK
    assert 'access' in response.data  # Zamiast 'token', szukamy 'access' (standardowy klucz dla JWT)
    assert response.data['access'] is not None  # Token JWT nie może być pusty

@pytest.mark.django_db
def test_user_login_invalid_credentials():
    client = APIClient()
    data = {
        'username': 'wronguser',  # Błędna nazwa użytkownika
        'password': 'wrongpassword'  # Błędne hasło
    }

    # Wysłanie żądania logowania
    response = client.post(reverse('login'), data, format='json')

    # Sprawdzamy, czy odpowiedź zawiera status 401 i odpowiedni komunikat
    assert response.status_code == status.HTTP_401_UNAUTHORIZED
    assert 'detail' in response.data
    assert response.data['detail'] == 'No active account found with the given credentials'  # Zaktualizowany komunikat 