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
        return PlayerCharacter.objects.select_related('user').filter(
            user=self.request.user
        )
    
    def perform_create(self, serializer):
        serializer.save(user=self.request.user)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # 🔥 wybór istniejącej postaci (stabilny)
        character = (
            PlayerCharacter.objects
            .filter(user=user)
            .order_by("-updated_at", "-id")
            .first()
        )

        # 🔥 fallback jeśli user nie ma postaci
        if not character:
            character = PlayerCharacter.objects.create(
                user=user,
                name=f"{user.username}_hero",
                level=1,
                experience=0,
                health=100,
                max_health=100,
                mana=50,
                max_mana=50,
                strength=10,
                dexterity=10,
                intelligence=10,
            )

        return Response({
            "user": {
                "id": user.id,
                "username": user.username,
                "email": user.email,
            },
            "character": PlayerCharacterSerializer(character).data
        })