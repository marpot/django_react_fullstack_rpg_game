import jwt
from django.conf import settings

def decode_jwt(token):
    try:
        return jwt.decode(token, settings.SECRET_KEY, algorithms=["HS256"])
    except Exception:
        return None
