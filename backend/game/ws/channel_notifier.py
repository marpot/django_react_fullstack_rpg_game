from asgiref.sync import async_to_sync
from channels.layers import get_channel_layer


class GameChannelNotifier:

    def emit(self, room_id, message):
        payload = message.get("payload") or {}
        world = payload.get("world") or {}
        intro = payload.get("intro") or {}

        text = message.get("text")
        if not text and isinstance(intro, dict):
            text = intro.get("text")
        if not text:
            text = world.get("intro") or world.get("description") or "The adventure has begun."

        channel_layer = get_channel_layer()
        async_to_sync(channel_layer.group_send)(
            f"gameconsumer_{room_id}",
            {
                "type": "game_event",
                "event": message.get("event", "game_started"),
                "payload": payload,
                "text": text,
            },
        )
