from rest_framework import serializers
from .models import GameSession, GameEvent

class GameSessionSerializer(serializers.ModelSerializer):
    player_id = serializers.IntegerField(source='player.id', read_only=True)
    player_name = serializers.CharField(source='player.name', read_only=True)

    class Meta:
        model = GameSession
        fields = ["id", "player_id", "player_name", "progress", "created_at", "updated_at"]
        read_only_fields = ('created_at', 'updated_at')

class GameEventSerializer(serializers.ModelSerializer):
    player_id = serializers.IntegerField(source='player.id', read_only=True)
    adventure_id = serializers.IntegerField(source='adventure.id', read_only=True)
    location_id = serializers.IntegerField(source='location.id', read_only=True)

    class Meta:
        model = GameEvent
        fields = [
            "id",
            "player_id",
            "adventure_id",
            "location_id",
            "description",
            "event_type",
            "timestamp",
            "required_flags",
            "blocking_flags",
            "requirements",
            "event_data",
            "choices",
            "consequences"
        ]
        
        read_only_fields = ('timestamp',)

    def create(self, validated_data):
        # Inicjalizacja choices jeśli nie są podane
        if 'choices' not in validated_data:
            validated_data['choices'] = []
        return super().create(validated_data)

    
