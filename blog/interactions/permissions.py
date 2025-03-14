from rest_framework import permissions
from .models import Comment
from posts.models import BlogPost


class CommentPermission(permissions.BasePermission):
    """
    Permiso personalizado para controlar las acciones de los comentarios.
    """
    def has_object_permission(self, request, view, obj):
        user = request.user

        # Solo el autor del comentario puede editarlo o eliminarlo
        if request.method in permissions.SAFE_METHODS:
            return True
        else:
            if isinstance(obj, BlogPost): 
                return obj.author == user or user.groups.exists() and obj.author.groups.filter(id__in=user.groups.values_list("id", flat=True)).exists()

            if isinstance(obj, Comment):  
                return obj.user == user or user.groups.exists() and obj.user.groups.filter(id__in=user.groups.values_list("id", flat=True)).exists()