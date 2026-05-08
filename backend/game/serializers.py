from rest_framework import serializers
from .models import GameSession, GameEvent
from accounts.models import PlayerCharacter

class GameSessionSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameSession
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

class GameEventSerializer(serializers.ModelSerializer):
    class Meta:
        model = GameEvent
        fields = '__all__'
        read_only_fields = ('timestamp',)

    def create(self, validated_data):
        # Inicjalizacja choices jeśli nie są podane
        if 'choices' not in validated_data:
            validated_data['choices'] = []
        return super().create(validated_data)

    def add_choice(self, choice_data):
        if not isinstance(choice_data, dict):
            raise serializers.ValidationError("Choice data must be a dictionary")
        choices = self.instance.choices
        choices.append(choice_data)
        self.instance.choices = choices
        self.instance.save()

