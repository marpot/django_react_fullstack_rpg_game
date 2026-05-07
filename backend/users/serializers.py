from rest_framework import serializers
from django.contrib.auth import get_user_model
import logging

User = get_user_model()
logger = logging.getLogger(__name__)


# =========================
# REGISTER
# =========================
class UserRegisterSerializer(serializers.ModelSerializer):
    username = serializers.CharField()
    email = serializers.EmailField(required=True)
    password = serializers.CharField(write_only=True)

    class Meta:
        model = User
        fields = ['username', 'email', 'password']

    def create(self, validated_data):
        user = User.objects.create_user(
            username=validated_data["username"],
            email=validated_data["email"],
            password=validated_data["password"],
        )
        return user


# =========================
# LOGIN
# =========================
class UserLoginSerializer(serializers.Serializer):
    username = serializers.CharField(required=False, allow_blank=True)
    email = serializers.EmailField(required=False, allow_blank=True)
    password = serializers.CharField()

    def validate(self, attrs):
        username = attrs.get("username")
        email = attrs.get("email")
        password = attrs.get("password")

        if not password:
            raise serializers.ValidationError("Password is required")

        if not username and not email:
            raise serializers.ValidationError(
                "Provide either username or email"
            )

        user = None

        # 🔥 LOGIN BY EMAIL
        if email:
            user = User.objects.filter(email=email).first()

        # 🔥 LOGIN BY USERNAME
        else:
            user = User.objects.filter(username=username).first()

        # 🔐 PASSWORD CHECK
        if not user or not user.check_password(password):
            raise serializers.ValidationError("Invalid credentials")

        return {"user": user}