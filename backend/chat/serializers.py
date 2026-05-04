from rest_framework import serializers
import logging

from .models import Room
from world.models import Adventure

logger = logging.getLogger(__name__)


class RoomSerializer(serializers.ModelSerializer):

    adventure = serializers.PrimaryKeyRelatedField(
        queryset=Adventure.objects.all(),
        required=False,
        allow_null=True
    )

    adventure_title = serializers.CharField(
        source='adventure.title',
        read_only=True,
        allow_null=True
    )

    class Meta:
        model = Room
        fields = '__all__'
        read_only_fields = ('owner', 'created_at')

    def to_internal_value(self, data):
        logger.info(f"to_internal_value - otrzymane dane: {data}")

        if 'adventure' in data and data['adventure'] is None:
            data.pop('adventure')

        return super().to_internal_value(data)

    def validate(self, data):

        if 'name' in data:

            qs = Room.objects.filter(name=data['name'])

            if self.instance:
                qs = qs.exclude(id=self.instance.id)

            if qs.exists():
                raise serializers.ValidationError({
                    "name": "Pokój o tej nazwie już istnieje"
                })

        return data