from rest_framework.views import APIView
from rest_framework import viewsets
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from rest_framework.response import Response
from rest_framework.decorators import action
import logging

from .models import Room
from .serializers import RoomSerializer

logger = logging.getLogger(__name__)

class RoomViewSet(viewsets.ModelViewSet):
    queryset = Room.objects.all()
    serializer_class = RoomSerializer
    permission_classes = [IsAuthenticated] 

    def create(self, request, *args, **kwargs):
        logger.info(f"Metoda: {request.method}")
        logger.info(f"Content-Type: {request.content_type}")
        logger.info(f"User: {request.user}")
        logger.info(f"Data: {request.data}")
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        logger.info(f"Próba utworzenia pokoju przez użytkownika: {self.request.user}")
        logger.info(f"Otrzymane dane: {self.request.data}")
        try:
            room = serializer.save(owner=self.request.user)
            logger.info(f"Pokój utworzony pomyślnie: {room.name}")
        except Exception as e:
            logger.error(f"Błąd podczas tworzenia pokoju: {str(e)}")
            raise
        
    @action(detail=True, methods=['post'], permission_classes=[IsAuthenticated])
    def start_game(self, request, pk=None):
        room = self.get_object()

        if room.owner != request.user:
            raise PermissionDenied("Only the room owner can start the game.")
        
        room.state = "in_game"
        room.save()
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
        

