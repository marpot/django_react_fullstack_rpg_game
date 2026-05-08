import pytest
from channels.testing import WebsocketCommunicator
from django.contrib.auth import get_user_model
from django.test import TransactionTestCase
from django.conf import settings

from rpg_project.asgi import application
from chat.consumers_modules.chat_consumer import ChatConsumer
import jwt


User = get_user_model()


@pytest.mark.asyncio
class ChatConsumerTests(TransactionTestCase):

    async def create_user_and_token(self):
        user = await User.objects.acreate(
            username="testuser",
            email="test@test.com"
        )

        token = jwt.encode(
            {"user_id": user.id},
            settings.SECRET_KEY,
            algorithm="HS256"
        )

        return user, token

    async def test_chat_message_flow(self):
        user, token = await self.create_user_and_token()

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
        assert response["username"] == "testuser"

        await communicator.disconnect()

    async def test_reject_invalid_token(self):
        communicator = WebsocketCommunicator(
            application,
            "/ws/chat/lobby/?token=invalid"
        )

        connected, _ = await communicator.connect()

        assert connected is False