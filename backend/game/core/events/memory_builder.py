from game.models import GameEvent


class GameMemoryBuilder:
    def build(self, adventure_id: int, room_id: str, limit: int = 20):
        events = (
            GameEvent.objects
            .filter(adventure_id=adventure_id)
            .order_by("-timestamp")[:limit]
        )

        history = []

        for e in reversed(events):
            history.append({
                "type": e.event_type,
                "description": e.description,
                "player": getattr(e.player, "id", None),
                "location": getattr(e.location, "id", None),
                "choices": e.choices or []
            })

        return {
            "events": history,
            "count": len(history),
            "adventure_id": adventure_id,
            "room_id": room_id,
        }