import pytest
from channels.testing import WebsocketCommunicator
from rpg_project.asgi import application


@pytest.mark.asyncio
class GameConsumerTests:

    async def test_move_action(self):
        communicator = WebsocketCommunicator(
            application,
            "/ws/game/lobby/?token=VALID_TOKEN"
        )

        await communicator.connect()

        await communicator.send_json_to({
            "action": "move",
            "sender": "Player1"
        })

        response = await communicator.receive_json_from()

        assert "porusza się" in response["message"]

        await communicator.disconnect()