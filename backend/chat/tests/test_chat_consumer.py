import pytest
import jwt

from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model
from django.conf import settings
from asgiref.sync import sync_to_async

from rpg_project.asgi import application


User = get_user_model()


@pytest.mark.django_db
@pytest.mark.asyncio
class ChatConsumerTests:

    @pytest.fixture
    def user(self):
        return User.objects.create(
            username="testuser",
            email="test@test.com"
        )

    def create_token(self, user):
        return jwt.encode(
            {"user_id": user.id},
            settings.SECRET_KEY,
            algorithm="HS256"
        )

    @pytest.mark.asyncio
    async def test_chat_message_flow(self, user):
        token = self.create_token(user)

        communicator = WebsocketCommunicator(
            application,
            f"/ws/chat/lobby/?token={token}"
        )

        connected, _ = await communicator.connect()
        assert connected is True

        await communicator.send_json_to({
            "message": "Hello world"
        })

        response = await communicator.receive_json_from()
        assert response["message"] == "Hello world"

        await communicator.disconnect()

    @pytest.mark.asyncio
    async def test_reject_invalid_token(self):
        communicator = WebsocketCommunicator(
            application,
            "/ws/chat/lobby/?token=invalid"
        )

        connected, _ = await communicator.connect()
        assert connected is False