from django.urls import path, include
from rest_framework.routers import DefaultRouter
from accounts.views import PlayerCharacterViewSet
from users.views import UserRegisterView, UserLoginView
from rest_framework_simplejwt.views import TokenRefreshView

router = DefaultRouter()
router.register(r'characters', PlayerCharacterViewSet, basename='characters')


urlpatterns = [
	path('register/', UserRegisterView.as_view(), name='register'),
	path('login/', UserLoginView.as_view(), name='login'),
	path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
	path('', include(router.urls)),
]