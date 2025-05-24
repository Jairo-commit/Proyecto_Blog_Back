from django.contrib.auth.models import User
from rest_framework import viewsets
from .serializers import UserSerializer, UserCreateSerializer

# Create your views here.

class UserViewSet(viewsets.ReadOnlyModelViewSet):
    """ Vista de solo lectura para listar y ver usuarios. """
    queryset = User.objects.all()
    serializer_class = UserSerializer


class UserCreateViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserCreateSerializer

    def get_queryset(self):
        return User.objects.none()  # Evita exponer todos los usuarios
