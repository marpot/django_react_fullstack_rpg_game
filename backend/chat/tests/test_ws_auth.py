import pytest
import jwt

from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model
from django.conf import settings

from rpg_project.asgi import application

User = get_user_model()


@pytest.mark.asyncio
class WebSocketAuthTests:

    async def create_user_and_token(self):
        user = await User.objects.acreate(
            username="auth_user"
        )

        token = jwt.encode(
            {"user_id": user.id},
            settings.SECRET_KEY,
            algorithm="HS256"
        )

        return user, token

    async def test_valid_token_accepts_connection(self):
        _, token = await self.create_user_and_token()

        communicator = WebsocketCommunicator(
            application,
            f"/ws/chat/lobby/?token={token}"
        )

        connected, _ = await communicator.connect()
        assert connected is True

        await communicator.disconnect()

    async def test_invalid_token_rejected(self):
        communicator = WebsocketCommunicator(
            application,
            "/ws/chat/lobby/?token=invalid"
        )

        connected, _ = await communicator.connect()
        assert connected is False