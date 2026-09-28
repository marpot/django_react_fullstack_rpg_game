import logging
from urllib.parse import parse_qs

from channels.db import database_sync_to_async
from django.conf import settings
from django.contrib.auth import get_user_model
from django.contrib.auth.models import AnonymousUser
from jwt import decode as jwt_decode
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework_simplejwt.tokens import UntypedToken

logger = logging.getLogger(__name__)


class JWTAuthMiddleware:
    def __init__(self, app):
        self.app = app

    async def __call__(self, scope, receive, send):
        scope["user"] = await self._authenticate(scope)
        return await self.app(scope, receive, send)

    async def _authenticate(self, scope):
        token = self._get_token(scope)
        if not token:
            return AnonymousUser()

        try:
            UntypedToken(token)
            payload = jwt_decode(
                token,
                settings.SECRET_KEY,
                algorithms=["HS256"],
            )
            user_id = payload.get("user_id")
            if not user_id:
                return AnonymousUser()
            return await self._get_user(user_id)
        except (InvalidToken, TokenError, KeyError):
            return AnonymousUser()
        except Exception:
            logger.exception("Unexpected WebSocket authentication error")
            return AnonymousUser()

    def _get_token(self, scope):
        query_string = scope.get("query_string", b"").decode()
        params = parse_qs(query_string)
        token = params.get("token")
        return token[0] if token else None

    @database_sync_to_async
    def _get_user(self, user_id):
        User = get_user_model()
        return User.objects.filter(id=user_id).first()
