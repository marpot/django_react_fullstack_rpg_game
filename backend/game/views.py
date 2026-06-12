from rest_framework import viewsets, filters
from rest_framework.decorators import action
from rest_framework.response import Response

import traceback

from .models import GameSession, GameEvent
from .serializers import GameSessionSerializer, GameEventSerializer

from simulation_engine.services.combat_service import CombatService
from simulation_engine.services.dice_service import DiceService

class GameSessionViewSet(viewsets.ModelViewSet):

    queryset = GameSession.objects.all()
    serializer_class = GameSessionSerializer

    def _resolve_fight(self, attacker, defender):
        dice = DiceService(seed=1)
        combat = CombatService(dice)
        return combat.resolve(attacker, defender)

    @action(detail=True, methods=['post'])
    def fight(self, request, pk=None):
        try:
            session = self.get_object()

            attacker = session.player
            defender_name = request.data.get("enemy")

            if not attacker:
                return Response({"error": "Missing attacker"}, status=400)

            if not defender_name:
                return Response({"error": "Missing enemy"}, status=400)

            # =========================
            # ADVENTURE SOURCE OF TRUTH
            # =========================
            adventure_id = getattr(session, "adventure_id", None)

            if not adventure_id:
                return Response(
                    {"error": "GameSession missing adventure_id"},
                    status=400
                )

            # =========================
            # ADAPTER ORM -> COMBAT RUNTIME
            # =========================
            attacker_runtime = type("AttackerRuntime", (), {})()
            attacker_runtime.id = attacker.id
            attacker_runtime.name = getattr(attacker, "name", "hero")

            attacker_runtime.attack_bonus = getattr(attacker, "strength", 0) // 2
            attacker_runtime.defense = getattr(attacker, "dexterity", 0) // 2
            attacker_runtime.damage_die = 6
            attacker_runtime.damage_bonus = getattr(attacker, "strength", 0) // 3
            attacker_runtime.hp = getattr(attacker, "health", 100)

            defender_runtime = type("EnemyRuntime", (), {})()
            defender_runtime.name = defender_name
            defender_runtime.attack_bonus = 2
            defender_runtime.defense = 10
            defender_runtime.damage_die = 6
            defender_runtime.damage_bonus = 1
            defender_runtime.hp = 30

            result = self._resolve_fight(attacker_runtime, defender_runtime)

            GameEvent.objects.create(
                player=session.player,
                adventure_id=adventure_id,
                description=f"Fight result: {result.winner}",
                event_type="combat",
                event_data={
                    "attacker_damage": result.attacker_damage,
                    "defender_damage": result.defender_damage,
                    "winner": result.winner,
                }
            )

            return Response({
                "result": result.__dict__,
            })

        except Exception as e:
            print("FIGHT VIEW ERROR:", repr(e))
            traceback.print_exc()
            return Response(
                {"error": str(e)},
                status=500
            )


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
        