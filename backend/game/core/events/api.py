from rest_framework.views import APIView # pyright: ignore[reportMissingImports]
from rest_framework.response import Response # pyright: ignore[reportMissingImports]

from game.core.events.service import GameEventService
from game.serializers import GameEventSerializer


class GameEventHistoryView(APIView):
    def get(self, request, room_id: int):

        events = GameEventService.get_history(room_id)


        return Response({
            "events": GameEventSerializer(events, many=True).data
        })