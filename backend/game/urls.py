from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import GameSessionViewSet, GameEventViewSet

router = DefaultRouter()
router.register(r'sessions', GameSessionViewSet)
router.register(r'events', GameEventViewSet)

urlpatterns = [
    path('', include(router.urls)),
]