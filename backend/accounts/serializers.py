from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import PlayerCharacter
import logging

logger = logging.getLogger(__name__)
User = get_user_model()

class CharacterSummarySerializer(serializers.ModelSerializer):
    class Meta:
        """
            Lightweight serializer used for:
            - profile page
            - character selection screen
            - dashboard lists

            Purpose:
            Avoid sending full RPG state (stats, JSON fields, relations)
            when only summary information is needed by UI.
        """

        model = PlayerCharacter
        fields = ['id', 'name', 'level', 'is_active', 'health', 'max_health']

class PlayerCharacterSerializer(serializers.ModelSerializer):
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = PlayerCharacter
        fields = [
            "id",
            "username",
            "email",

            "name",
            "level",
            "experience",

            "health",
            "max_health",
            "mana",
            "max_mana",

            "strength",
            "dexterity",
            "intelligence",

            "adventure",
            "current_location",

            "created_at",
            "updated_at",
        ]

        read_only_fields = ('created_at', 'updated_at')

    def validate(self, data):
        health = data.get('health')
        max_health = data.get('max_health')


        if health is not None and max_health is not None:
            if health > max_health:
                raise serializers.ValidationError({
                    "health": "Health cannot exceed max health"
                })
            
            mana = data.get('mana')
            max_mana = data.get('max_mana')

            if mana is not None and max_mana is not None:
                if mana > max_mana:
                    raise serializers.ValidationError({
                        "mana": "Mana cannot exceed max mana"
                    })
        return data


class UserRegisterSerializer(serializers.ModelSerializer):
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

    def validate(self, attrs):
        if User.objects.filter(username=attrs['username']).exists():
            raise serializers.ValidationError({"username": "Username already exists"})
        
        if User.objects.filter(email=attrs['email']).exists():
            raise serializers.ValidationError({"email": "Email already exists"})
            
        return attrs

#LEGACY CODE - DO NOT DELETE
# class UserLoginSerializer(serializers.Serializer):
#     username = serializers.CharField(required=False, allow_blank=True)
#     email = serializers.EmailField(required=False, allow_blank=True)
#     password = serializers.CharField()

#     def validate(self, attrs):
#         username = attrs.get("username")
#         email = attrs.get("email")
#         password = attrs.get("password")

#         logger.info(f"LOGIN ATTEMPT: username={username}, email={email}")

#         if not password:
#             logger.warning("LOGIN FAILED: missing password")
#             raise serializers.ValidationError({"detail": "Password is required"})

#         if not username and not email:
#             logger.warning("LOGIN FAILED: missing identifier")
#             raise serializers.ValidationError({
#                 "detail": "Provide username or email"
#             })

#         user = None

#         if email:
#             user = User.objects.filter(email=email).first()
#         else:
#             user = User.objects.filter(username=username).first()

#         if not user:
#             logger.warning(f"LOGIN FAILED: user not found ({username or email})")
#             raise serializers.ValidationError({
#                 "detail": "Invalid credentials"
#             })

#         if not user.check_password(password):
#             logger.warning(f"LOGIN FAILED: wrong password ({user.username})")
#             raise serializers.ValidationError({
#                 "detail": "Invalid credentials"
#             })

#         logger.info(f"LOGIN SUCCESS: user_id={user.id}")

#         return {
#             "user": user
#         }