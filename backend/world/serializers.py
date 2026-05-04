from rest_framework import serializers
from .models import Adventure, Location, Choice

class AdventureSerializer(serializers.ModelSerializer):
    class Meta:
        model = Adventure
        fields = '__all__'
        read_only_fields = ['creator']

class LocationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Location
        fields = '__all__'

class ChoiceSerializer(serializers.ModelSerializer):
    class Meta:
        model = Choice
        fields = '__all__'