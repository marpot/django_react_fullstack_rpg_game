from urllib.parse import parse_qs

from channels.middleware import BaseMiddleware
from channels.db import database_sync_to_async

from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from django.conf import settings

from rest_framework_simplejwt.tokens import UntypedToken
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from jwt import decode as jwt_decode


class JWTAuthMiddleware(BaseMiddleware):

    async def __call__(self, scope, receive, send):
        scope["user"] = await self._authenticate(scope)
        return await super().__call__(scope, receive, send)

    async def _authenticate(self, scope):
        token = self._get_token(scope)
        if not token:
            return AnonymousUser()

        try:
            # 1. walidacja tokena (exp, signature)
            UntypedToken(token)

            # 2. decode payload
            payload = jwt_decode(
                token,
                settings.SECRET_KEY,
                algorithms=["HS256"]
            )

            user_id = payload.get("user_id")
            if not user_id:
                return AnonymousUser()

            return await self._get_user(user_id)

        except (InvalidToken, TokenError, KeyError):
            return AnonymousUser()

    def _get_token(self, scope):
        query_string = scope.get("query_string", b"").decode()
        params = parse_qs(query_string)
        token = params.get("token")
        return token[0] if token else None

    @database_sync_to_async
    def _get_user(self, user_id):
        User = get_user_model()
        try:
            return User.objects.get(id=user_id)
        except User.DoesNotExist:
            return AnonymousUser()