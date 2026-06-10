import json
from .base import BaseConsumer


class ChatConsumer(BaseConsumer):

    async def receive(self, text_data):
        data = json.loads(text_data)
        message = data.get("message", "").strip()
        if not message:
            return

        user = self.scope["user"]
        username = user.username if user.is_authenticated else "Anonim"

        await self.send_event(
            "chat_message",
            {
                "message": message,
                "username": username,
            }
        )

    async def chat_message(self, event):
        await self.send(text_data=json.dumps({
            "type": "chat_message",
            **event["payload"]
        }))