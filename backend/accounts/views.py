from rest_framework import viewsets
from .models import PlayerCharacter
from .serializers import PlayerCharacterSerializer


class PlayerCharacterViewSet(viewsets.ModelViewSet):
    serializer_class = PlayerCharacterSerializer
    queryset = PlayerCharacter.objects.all()

    def get_queryset(self):
        return PlayerCharacter.objects.filter(user=self.request.user)