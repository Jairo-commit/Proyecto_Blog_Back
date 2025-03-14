from django.urls import path
from rest_framework.routers import DefaultRouter
from .viewsets import UserViewSet, UserCreateViewSet



router = DefaultRouter()

router.register('users', UserViewSet)
router.register('register', UserCreateViewSet, basename='user_register')

urlpatterns =  router.urls
