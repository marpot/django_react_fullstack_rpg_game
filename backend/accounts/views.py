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


class SelectActiveCharacterView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        character_id = request.data.get("character_id")

        try:
            character = PlayerCharacter.objects.get(
                id=character_id,
                user=request.user
            )
            
            # deactivate all
            PlayerCharacter.objects.filter(
                user=request.user
            ).update(is_active=False)

            # activate selected
            character.is_active = True
            character.save()

            return Response({
                "active_character_id": character.id,
                "character_name": character.name
            })

        except PlayerCharacter.DoesNotExist:
            return Response({
                "error": "Nie znaleziono postaci"
            }, status=404)


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user

        # 1. active character
        character = PlayerCharacter.objects.filter(
            user=user,
            is_active=True
        ).first()

        # 2. fallback to any character
        if not character:
            character = PlayerCharacter.objects.filter(user=user).first()

            # 3. auto-fix: ensure at least one active
            if character:
                character.is_active = True
                character.save()

        # 4. create default if none exists
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
            "character": PlayerCharacterSerializer(character).data,
            "characters": PlayerCharacterSerializer(
                PlayerCharacter.objects.filter(user=user),
                many=True
            ).data
        })