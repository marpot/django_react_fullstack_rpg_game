import jwt
from jwt import ExpiredSignatureError, DecodeError
from django.conf import settings
from django.contrib.auth import get_user_model
from urllib.parse import parse_qs
from channels.generic.websocket import AsyncWebsocketConsumer
import json


class BaseConsumer(AsyncWebsocketConsumer):

    async def connect(self):
        self.room_name = self.scope["url_route"]["kwargs"]["room_name"]
        self.room_group_name = self.get_room_group_name()

        token = self.get_token_from_query_string()

        if not token:
            await self.close(code=4001)
            return

        try:
            user = await self.authenticate_user(token)

        except ExpiredSignatureError:
            await self.close(code=4002)
            return

        except DecodeError:
            await self.close(code=4003)
            return

        except Exception:
            await self.close(code=4004)
            return

        self.scope["user"] = user

        await self.accept()

        await self.channel_layer.group_add(
            self.room_group_name,
            self.channel_name
        )

        await self.on_connect()

    def get_token_from_query_string(self):
        query_string = parse_qs(self.scope["query_string"].decode())
        return query_string.get("token", [None])[0]

    async def authenticate_user(self, token):
        payload = jwt.decode(
            token,
            settings.SECRET_KEY,
            algorithms=["HS256"]
        )

        User = get_user_model()

        try:
            return await User.objects.aget(id=payload["user_id"])
        except User.DoesNotExist:
            raise Exception("USER_NOT_FOUND")

    def get_room_group_name(self):
        return f"{self.__class__.__name__.lower()}_{self.room_name}"

    async def on_connect(self):
        pass

    async def disconnect(self, close_code):
        await self.channel_layer.group_discard(
            self.room_group_name,
            self.channel_name
        )

    async def receive(self, text_data):
        raise NotImplementedError

    async def chat_message(self, event):
        message = event.get("message")
        username = event.get("username")

        await self.send(text_data=json.dumps({
            "message": message,
            "username": username
            }))

    async def send_message(self, message, username):
        await self.channel_layer.group_send(
            self.room_group_name,
            {
                "type": "chat_message",
                "message": message,
                "username": username,
            }
        )