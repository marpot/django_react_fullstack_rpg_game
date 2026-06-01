from django.urls import path, include
from rest_framework.routers import DefaultRouter
from accounts.views import PlayerCharacterViewSet
from users.views import UserRegisterView, UserLoginView
from rest_framework_simplejwt.views import TokenRefreshView

from .views import MeView, SelectActiveCharacterView

router = DefaultRouter()
router.register(r'characters', PlayerCharacterViewSet, basename='characters')


urlpatterns = [
    path("select-active-character/", SelectActiveCharacterView.as_view(), name="select-active-character"),
	path('register/', UserRegisterView.as_view(), name='register'),
	path('login/', UserLoginView.as_view(), name='login'),
	path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
	path('me/', MeView.as_view(), name='me'),
	path('', include(router.urls)),
]