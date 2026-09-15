from rest_framework import serializers
import logging

from .models import Room, RoomParticipant
from world.models import Adventure

logger = logging.getLogger(__name__)


class RoomParticipantSerializer(serializers.ModelSerializer):
    participant_id = serializers.IntegerField(source="id", read_only=True)
    character_id = serializers.IntegerField(read_only=True)
    is_current_user = serializers.SerializerMethodField()

    class Meta:
        model = RoomParticipant
        fields = (
            "participant_id",
            "character_id",
            "name",
            "is_ai",
            "is_current_user",
        )

    def get_is_current_user(self, obj):
        request = self.context.get("request")
        return bool(
            request
            and request.user.is_authenticated
            and obj.user_id == request.user.id
        )


class SelectRoomCharacterSerializer(serializers.Serializer):
    character_id = serializers.IntegerField(min_value=1)


class RoomSerializer(serializers.ModelSerializer):

    adventure = serializers.PrimaryKeyRelatedField(
        queryset=Adventure.objects.all(),
        required=False,
        allow_null=True
    )

    adventure_title = serializers.SerializerMethodField()
    owner_id = serializers.IntegerField(source='owner.id', read_only=True)
    participants = RoomParticipantSerializer(many=True, read_only=True)

    class Meta:
        model = Room
        fields = '__all__'
        read_only_fields = ('owner', 'created_at')

    def get_adventure_title(self, obj):
        return obj.adventure.title if obj.adventure else None

    def validate(self, data):
        request = self.context.get("request")

        if 'name' in data:
            qs = Room.objects.filter(name=data['name'])

            if self.instance:
                qs = qs.exclude(id=self.instance.id)

            if qs.exists():
                raise serializers.ValidationError({
                    "name": "Pokój o tej nazwie już istnieje"
                })

        return data

    def create(self, validated_data):
        logger.info(f"[SERIALIZER CREATE] validated_data={validated_data}")
        return super().create(validated_data)
