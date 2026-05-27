from django.db import transaction
from typing import Optional, Dict, Any, List
from game.models import GameEvent


class GameEventService:
    @staticmethod
    def get_history(adventure_id: int):
        return (
            GameEvent.objects
            .filter(adventure_id=adventure_id)
            .select_related('player', 'location')
            .order_by('-timestamp')
        )

    @staticmethod
    @transaction.atomic
    def create_event(
        adventure,
        player,
        location,
        description: str,
        event_type: str,
        choices: Optional[List[Dict[str, Any]]] = None
    ) -> GameEvent:
        return GameEvent.objects.create(
            adventure=adventure,
            player=player,
            location=location,
            description=description,
            event_type=event_type,
            choices=choices or []
        )

    @staticmethod
    @transaction.atomic
    def add_choice(event: GameEvent, choice_data: Dict[str, Any]) -> GameEvent:
        event.choices = (event.choices or []) + [choice_data]
        event.save(update_fields=['choices'])
        return event