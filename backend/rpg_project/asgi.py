import os
from django.core.asgi import get_asgi_application
from channels.routing import ProtocolTypeRouter, URLRouter
from game.middleware.state_middleware import StateMiddleware

os.environ.setdefault("DJANGO_SETTINGS_MODULE", "rpg_project.settings")

django_asgi_app = get_asgi_application()

from chat.routing import websocket_urlpatterns
from chat.middleware import JWTAuthMiddleware  # <- dopiero tutaj (PO init)

application = ProtocolTypeRouter({
    "http": django_asgi_app,
    "websocket": JWTAuthMiddleware(
        StateMiddleware(
            URLRouter(websocket_urlpatterns)
        )
    ),
})