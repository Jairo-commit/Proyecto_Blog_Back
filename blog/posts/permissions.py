from rest_framework import permissions
from posts.models import BlogPost
from django.db.models import Q

class BlogPostPermission(permissions.BasePermission):

    def has_object_permission(self, request, view, obj):
        """
        Verifica si el usuario tiene permiso para acceder a un BlogPost específico.
        - Permite "SAFE_METHODS" (GET, HEAD, OPTIONS) si el usuario tiene permisos de lectura.
        - Permite edición (POST, PUT, DELETE) solo si el usuario tiene permisos de edición.
        """

        user = request.user
        action = "Read and Edit" if request.method not in permissions.SAFE_METHODS else "Read"

        # Si el usuario es superusuario o staff, tiene acceso total
        if user.is_superuser or user.is_staff:
            return True

        # Permisos de lectura
        if action == "Read":
            return (
                (obj.public_access == "Read") or
                (user.is_authenticated and (obj.authenticated_access == "Read" or obj.authenticated_access == "Read and Edit")) or
                (obj.author == user) or
                (user.groups.exists() and obj.author.groups.filter(id__in=user.groups.values_list("id", flat=True)).exists() and (obj.group_access == "Read" or obj.group_access == "Read and Edit"))
            )

        # Permisos de edición
        if action == "Read and Edit":
            return (
                (obj.author == user and obj.author_access == "Read and Edit") or
                (user.groups.exists() and obj.author.groups.filter(id__in=user.groups.values_list("id", flat=True)).exists() and obj.group_access == "Read and Edit") or
                (user.is_authenticated and obj.authenticated_access == "Read and Edit")
            )

        return False
