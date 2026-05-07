from rest_framework import viewsets, filters, serializers
from rest_framework.decorators import action
from rest_framework.response import Response

from .models import GameSession, GameEvent
from .serializers import GameSessionSerializer, GameEventSerializer

from game.services.combat_service import CombatService
from game.services.dice_service import DiceService


class GameSessionViewSet(viewsets.ModelViewSet):
    """
    GameSession API ViewSet.

    Handles lifecycle of game sessions and triggers gameplay actions.

    Responsibilities:
        - CRUD for GameSession
        - Trigger combat via /fight/ endpoint

    Endpoints:
        GET    /api/sessions/          - list sessions
        POST   /api/sessions/          - create session
        GET    /api/sessions/{id}/     - retrieve session
        PUT    /api/sessions/{id}/     - update session
        DELETE /api/sessions/{id}/     - delete session

    Custom actions:
        POST /api/sessions/{id}/fight/ - simulate combat encounter

    Notes:
        Business logic is delegated to service layer (CombatService).
        ViewSet only orchestrates request/response flow.
    """

    queryset = GameSession.objects.all()
    serializer_class = GameSessionSerializer

    def _resolve_fight(self, attacker, defender):
        """
        Resolves combat using service layer.

        Flow:
            - Initializes DiceService (Random Number Generator)
            - Passes dependencies to CombatService
            - Executes combat rules

        Returns:
            CombatResult: result of fight simulation
        """
        dice = DiceService(seed=1)
        combat = CombatService(dice)
        return combat.resolve(attacker, defender)

    @action(detail=True, methods=['post'])
    def fight(self, request, pk=None):
        """
        Triggers combat encounter for current session.

        Request:
            enemy - target entity (temporary placeholder)

        Process:
            1. Get session player
            2. Resolve combat via service layer
            3. Save result as GameEvent
            4. Return combat outcome

        Returns:
            JSON with CombatResult data
        """
        session = self.get_object()

        attacker = session.player
        defender = request.data.get("enemy")

        result = self._resolve_fight(attacker, defender)

        GameEvent.objects.create(
            player=session.player,
            description=f"Fight result: {result.winner}",
            event_type="combat",
            event_data={
                "attacker_damage": result.attacker_damage,
                "defender_damage": result.defender_damage,
            }
        )

        return Response({
            "result": result.__dict__,
        })


class GameEventViewSet(viewsets.ModelViewSet):
    """
    GameEvent API ViewSet.

    Provides access to game world events and supports:
        - filtering
        - searching
        - ordering
        - history retrieval

    Endpoints:
        GET    /api/events/
        GET    /api/events/{id}/
        POST   /api/events/
        PUT    /api/events/{id}/
        DELETE /api/events/{id}/

    Custom actions:
        GET  /api/events/history/
        POST /api/events/{id}/add_choice/
    """

    queryset = GameEvent.objects.all()
    serializer_class = GameEventSerializer

    filter_backends = [filters.SearchFilter, filters.OrderingFilter]
    search_fields = ['description', 'event_type']
    ordering_fields = ['timestamp']
    ordering = ['-timestamp']

    def get_queryset(self):
        """
        Filters events based on query parameters.

        Supported filters:
            - player (int)
            - adventure (int)
            - event_type (str)

        Returns:
            QuerySet[GameEvent]
        """
        queryset = GameEvent.objects.all()

        player_id = self.request.query_params.get('player')
        adventure_id = self.request.query_params.get('adventure')
        event_type = self.request.query_params.get('event_type')

        if player_id and not player_id.isdigit():
            raise serializers.ValidationError('Player ID must be integer')
        if adventure_id and not adventure_id.isdigit():
            raise serializers.ValidationError('Adventure ID must be integer')

        if player_id:
            queryset = queryset.filter(player_id=player_id)
        if adventure_id:
            queryset = queryset.filter(adventure_id=adventure_id)
        if event_type:
            queryset = queryset.filter(event_type=event_type)

        return queryset

    @action(detail=False, methods=['get'])
    def history(self, request):
        """
        Returns event history for specific location.

        Query params:
            location_id (int)

        Returns:
            List[GameEvent]
        """
        location_id = request.query_params.get('location_id')

        if location_id:
            events = GameEvent.objects.filter(location_id=location_id).order_by('-timestamp')
        else:
            events = GameEvent.objects.none()

        serializer = GameEventSerializer(events, many=True)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def add_choice(self, request, pk=None):
        """
        Adds a choice to a game event.

        Request body:
            text (str)
            next_location (int)
            consequences (dict)

        Endpoint:
            POST /api/events/{id}/add_choice/

        Delegates logic to serializer.
        """
        event = self.get_object()
        serializer = self.get_serializer(event)

        serializer.add_choice(request.data)

        return Response(serializer.data)