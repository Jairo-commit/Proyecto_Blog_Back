from rest_framework import permissions
from posts.models import BlogPost
from django.db.models import Q

#sirve para los get
class CommentPermission(permissions.BasePermission): 
    """
    Permisos de comentarios basados en la lógica de acceso de BlogPost.
    """

    def has_permission(self, request, view):
        user = request.user

        # 🔹 Superusuarios y staff pueden hacer cualquier acción
        if user.is_superuser or user.is_staff:
            return True

        # 🔹 Usuarios no autenticados solo pueden acceder a posts con `public_access="Read"`
        if not user.is_authenticated:
            post_id = view.kwargs.get("pk")
            return BlogPost.objects.filter(id=post_id, public_access="Read").exists()

        # 🔹 Usuarios autenticados pueden comentar en posts según las reglas de `get_queryset`
        query = Q(authenticated_access__in=["Read", "Read and Edit"]) | Q(author=user)
        
        user_groups = list(user.groups.all())
        if user_groups:
            query |= Q(group_access__in=["Read", "Read and Edit"], author__groups__in=user_groups)

        post_id = view.kwargs.get("pk")  # Obtiene el ID del post desde la URL
        return BlogPost.objects.filter(query, id=post_id).exists()

#sirve para los request post
class InteractionPermission(permissions.BasePermission):
    def has_permission(self, request, view):
        user = request.user
        if not user.is_authenticated:
            return False  # Solo usuarios autenticados pueden dar like
        
        if user.is_superuser or user.is_staff:
            return True
        
        post_id = view.kwargs.get("pk")
        return BlogPost.objects.filter(
        Q(id=post_id) & (
        Q(public_access="Read") | 
        Q(authenticated_access__in=["Read", "Read and Edit"]) |
        Q(author=user) |
        Q(group_access__in=["Read", "Read and Edit"], author__groups__in=user.groups.all())
        )
        ).exists()