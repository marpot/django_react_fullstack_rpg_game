from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import GameSession, GameEvent
from .serializers import GameSessionSerializer, GameEventSerializer

from game.models import Flag

from game.serializers import NPCSerializer
from game.npc.npc_resolver import NPCResolver



class GameSessionViewSet(viewsets.ModelViewSet):

    queryset = GameSession.objects.all()
    serializer_class = GameSessionSerializer

    @action(detail=True, methods=['get'])
    def npcs(self, request, pk=None):
        session = self.get_object()
        
        flags = Flag.objects.filter(
            adventure_id=session.progress.get("adventure_id"),
            player=session.player.user
        )

        resolver = NPCResolver(session)
        npcs = resolver.resolve()

        serializer = NPCSerializer(npcs, many=True)
        return Response(
            {
                "npcs": serializer.data
            })


class GameEventViewSet(viewsets.ModelViewSet):

    queryset = GameEvent.objects.all()
    serializer_class = GameEventSerializer

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['description', 'event_type']
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']

    def get_queryset(self):
        queryset = GameEvent.objects.all()

        player_id = self.request.query_params.get('player')
        adventure_id = self.request.query_params.get('adventure')
        event_type = self.request.query_params.get('event_type')

        if player_id:
            queryset = queryset.filter(player_id=player_id)
        if adventure_id:
            queryset = queryset.filter(adventure_id=adventure_id)
        if event_type:
            queryset = queryset.filter(event_type=event_type)

        return queryset

    @action(detail=False, methods=['get'])
    def history(self, request):
        location_id = request.query_params.get('location_id')

        if location_id:
            events = GameEvent.objects.filter(location_id=location_id).order_by('-timestamp')
        else:
            events = GameEvent.objects.none()

        serializer = GameEventSerializer(events, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_choice(self, request, pk=None):
        event = self.get_object()
        serializer = self.get_serializer(event)

        serializer.add_choice(request.data)

        return Response(serializer.data)
    
    @action(detail=False, methods=['get'])
    def current_session(self, request):
        player = request.user.playercharacter

        session = (GameSession.objects.filter(player=player).order_by('-created_at').first())

        if not session:
            return Response({"error": "No active session found"}, status=404)
        
        return Response(GameSessionSerializer(session).data)
