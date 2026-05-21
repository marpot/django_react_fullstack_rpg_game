from django.contrib.auth import get_user_model

from rest_framework.test import APITestCase
from rest_framework_simplejwt.tokens import RefreshToken

from accounts.models import PlayerCharacter

User = get_user_model()


class MeEndpointTests(APITestCase):

    def setUp(self):
        self.user = User.objects.create_user(
            username="testuser",
            email="test@example.com",
            password="testpass123"
        )

        self.character = PlayerCharacter.objects.create(
            user=self.user,
            name="Hero",
            level=1,
            experience=0,
            health=100,
            max_health=100,
            mana=50,
            max_mana=50,
            strength=10,
            dexterity=10,
            intelligence=10,
        )

    def authenticate(self):
        refresh = RefreshToken.for_user(self.user)

        self.client.credentials(
            HTTP_AUTHORIZATION=f"Bearer {refresh.access_token}"
        )

    def test_me_endpoint_returns_user_profile(self):
        self.authenticate()

        response = self.client.get("/api/accounts/me/")

        self.assertEqual(response.status_code, 200)

        self.assertEqual(
            response.data["user"]["username"],
            "testuser"
        )

        self.assertEqual(
            response.data["character"]["name"],
            "Hero"
        )

    def test_me_endpoint_requires_authentication(self):
        response = self.client.get("/api/accounts/me/")

        self.assertEqual(response.status_code, 401)