from rest_framework import serializers
from django.contrib.auth import get_user_model
from .models import PlayerCharacter
import logging

logger = logging.getLogger(__name__)
User = get_user_model()


class PlayerCharacterSerializer(serializers.ModelSerializer):
    class Meta:
        model = PlayerCharacter
        fields = '__all__'
        read_only_fields = ('created_at', 'updated_at')

    def validate(self, data):
        if data.get('health', 0) > data.get('max_health', 100):
            raise serializers.ValidationError("Health cannot exceed max_health")
        if data.get('mana', 0) > data.get('max_mana', 50):
            raise serializers.ValidationError("Mana cannot exceed max_mana")
        return data

    def create(self, validated_data):
        if 'equipment' not in validated_data:
            validated_data['equipment'] = {}
        if 'inventory' not in validated_data:
            validated_data['inventory'] = []
        if 'skills' not in validated_data:
            validated_data['skills'] = []
        if 'status_effects' not in validated_data:
            validated_data['status_effects'] = []
        if 'progress' not in validated_data:
            validated_data['progress'] = {}
        return super().create(validated_data)


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