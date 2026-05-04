import pytest
from django.urls import reverse
from rest_framework import status
from rest_framework.test import APIClient

@pytest.mark.django_db
def test_user_register():
    client = APIClient()
    data = {
        'username': 'testuser',
        'email': 'testuser@example.com',
        'password': 'testpassword123',
    }

    response = client.post(reverse('register'), data, format='json')

    assert response.status_code == status.HTTP_201_CREATED
    assert response.data['username'] == data['username']
    assert response.data['email'] == data['email'] 