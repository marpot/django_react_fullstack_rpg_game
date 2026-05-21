from rest_framework import viewsets
from .models import PlayerCharacter
from .serializers import PlayerCharacterSerializer
from rest_framework.permissions import IsAuthenticated

from rest_framework.views import APIView
from rest_framework.response import Response


class PlayerCharacterViewSet(viewsets.ModelViewSet):
    serializer_class = PlayerCharacterSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return PlayerCharacter.objects.select_related('user').filter(user=self.request.user)
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        character = PlayerCharacter.objects.filter(user=user).first()

        return Response({
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
            },
            "character": PlayerCharacterSerializer(character).data 
            if character is not None
            else None
        })