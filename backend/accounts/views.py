from rest_framework import viewsets
from .models import PlayerCharacter
from .serializers import PlayerCharacterSerializer
from rest_framework.permissions import IsAuthenticated


class PlayerCharacterViewSet(viewsets.ModelViewSet):
    serializer_class = PlayerCharacterSerializer
    permission_classes = [IsAuthenticated]
    queryset = PlayerCharacter.objects.all()

    def get_queryset(self):
        return PlayerCharacter.objects.select_related('user').filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)
    