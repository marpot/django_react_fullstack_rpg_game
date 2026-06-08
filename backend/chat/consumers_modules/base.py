import json
import logging
from channels.generic.websocket import AsyncWebsocketConsumer

logger = logging.getLogger("chat")


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
        print("CHANNEL:", self.channel_name)

        if not user or not user.is_authenticated:
            print("WS REJECTED: unauthenticated")
            await self.close(code=4003)
            return

        await self.accept()

        print("GROUP ADD:", self.room_group_name)

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        print("WS ACCEPTED + JOINED GROUP", self.room_group_name)

        await self.on_connect()

    def get_room_group_name(self):
        return f"{self.__class__.__name__.lower()}_{self.room_name}"

    async def on_connect(self):
        pass

    async def disconnect(self, close_code):
        print("WS DISCONNECT:", self.room_group_name)

        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        print("=== WS RECEIVE ===")
        print("RAW:", text_data)
        raise NotImplementedError

    async def chat_message(self, event):
        print("=== CHAT MESSAGE EVENT RECEIVED ===")
        print("EVENT:", event)

        await self.send(text_data=json.dumps({
            "message": event.get("message"),
            "username": event.get("username"),
        }))

    async def send_message(self, message, username):
        print("=== GROUP SEND ===")
        print("GROUP:", self.room_group_name)
        print("MSG:", message)

        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "username": username,
            }
        )