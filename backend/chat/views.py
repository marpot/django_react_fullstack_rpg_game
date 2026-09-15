from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.decorators import action

from chat.services.room_service import RoomService

import logging

from .models import Room
from .serializers import RoomSerializer

from game.middleware.state_middleware import STATE_MANAGER
from game.services.game_start_service import GameStartService
from game.ws.channel_notifier import GameChannelNotifier
from game_instances.services.llm.orchestrator.llm_service import LLMService
from world.seeders.world_seeder import WorldSeeder

logger = logging.getLogger(__name__)


class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticated]

    def create(self, request, *args, **kwargs):
        logger.info("========== ROOM CREATE ==========")
        logger.info(f"METHOD: {request.method}")
        logger.info(f"USER: {request.user}")
        logger.info(f"CONTENT_TYPE: {request.content_type}")
        logger.info(f"RAW DATA: {request.data}")
        logger.info("=================================")

        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        logger.info("========== PERFORM CREATE ==========")
        logger.info(f"USER: {self.request.user}")
        logger.info(f"REQUEST DATA: {self.request.data}")

        room = serializer.save(owner=self.request.user)

        logger.info("========== ROOM SAVED ==========")
        logger.info(f"ROOM ID: {room.id}")
        logger.info(f"ROOM ADVENTURE_ID: {room.adventure_id}")
        logger.info("================================")

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def set_adventure(self, request, pk=None):
        room = self.get_object()
        adventure_id = request.data.get("adventure_id")

        result = RoomService.set_adventure(room, request.user, adventure_id)

        if not result["ok"]:
            return Response(
                {"error": result["error"]},
                status=400
            )

        adventure = result["adventure"]

        return Response({
            "room_id": room.id,
            "adventure_id": adventure.id,
            "adventure_title": adventure.title
        })

    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def start_game(self, request, pk=None):
        logger.info("========== START GAME ==========")

        room = self.get_object()

        logger.info(f"ROOM ID: {room.id}")
        logger.info(f"ROOM STATE: {room.state}")
        logger.info(f"ROOM ADVENTURE_ID: {room.adventure_id}")

        if room.owner != request.user:
            raise PermissionDenied("Only the room owner can start the game.")

        if not room.adventure_id:
            return Response(
                {
                    "code": "NO_ADVENTURE",
                    "error": "Adventure must be selected before starting the game"
                },
                status=400
            )

        adventure = room.adventure

        logger.info(f"[START GAME] using adventure_id={adventure.id}")

        start_service = GameStartService(
            seeder=WorldSeeder(STATE_MANAGER),
            llm=LLMService(),
            notifier=GameChannelNotifier(),
            state_manager=STATE_MANAGER,
        )

        start_service.start_game(
            adventure_id=adventure.id,
            room_id=room.id,
            adventure=adventure,
        )

        room.state = "in_game"
        room.save(update_fields=["state"])

        logger.info("GAME START EVENT SENT")
        logger.info("================================")

        return Response(RoomSerializer(room).data)


class RoomDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, room_id):
        try:
            return Room.objects.get(id=room_id)
        except Room.DoesNotExist:
            raise PermissionDenied("The room does not exist.")

    def get(self, request, room_id):
        room = self.get_object(room_id)
        serializer = RoomSerializer(room)
        return Response(serializer.data)