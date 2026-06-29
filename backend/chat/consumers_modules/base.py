import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger("ws")


class BaseConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = self.get_room_group_name()

        user = self.scope.get("user")

        print("=== WS CONNECT ===")
        print("PATH:", self.scope["path"])
        print("ROOM:", self.room_name)
        print("GROUP:", self.room_group_name)
        print("USER:", user)

        if not user or not user.is_authenticated:
            print("WS REJECTED: unauthenticated")
            await self.close(code=4003)
            return

        await self.accept()

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.on_connect()

    def get_room_group_name(self):
        return f"{self.__class__.__name__.lower()}_{self.room_name}"

    async def on_connect(self):
        pass

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def send_event(self, event_type: str, payload: dict):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": event_type,
                "payload": payload
            }
        )

    async def _send_game_event(self, event_type: str, payload: dict, text: str = None):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "game_event",
                "event": event_type,
                "payload": payload,
                "text": text,
            }
        )

    # ✅ MUSI ISTNIEĆ (inaczej frontend NIC nie dostanie)
    async def game_event(self, event):
        await self.send(text_data=json.dumps(event))

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "message": event.get("message"),
            "username": event.get("username"),
        }))