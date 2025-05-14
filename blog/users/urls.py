from rest_framework.routers import DefaultRouter
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from django.urls import path

from .views import CurrentUserView
from .viewsets import UserViewSet, UserCreateViewSet


router = DefaultRouter()
router.register('users', UserViewSet, basename='users')
router.register('register', UserCreateViewSet, basename='user_register')


# Agregamos la ruta manual al final
urlpatterns = router.urls + [
    path('token/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('me/', CurrentUserView.as_view(), name='current_user'),
]