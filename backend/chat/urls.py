from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import RoomViewSet
from . import views

router = DefaultRouter()
router.register(r'rooms', RoomViewSet, basename='rooms')

urlpatterns = [
    path('', include(router.urls)),
]
