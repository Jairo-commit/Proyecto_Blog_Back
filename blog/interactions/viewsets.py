from django.shortcuts import get_object_or_404
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from django.contrib.auth.models import User

from .models import Comment, Like
from .permissions import CommentPermission
from .serializers import LikeSerializer, CommentSerializer
from .pagination import LikePagination, CommentPagination
from posts.models import BlogPost

# Create your views here.

class CommentViewSet(viewsets.ModelViewSet):
    """ Vista CRUD de comentarios. """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    pagination_class = CommentPagination

    def get_queryset(self):
        """ Filtra los likes según los permisos del usuario sobre los posts. """
        user = self.request.user

        if user.is_superuser or user.is_staff:
            return Comment.objects.all()

        if not user.is_authenticated:
            accessible_posts = BlogPost.objects.filter(public_access__in=["Read", "Read and Edit"])
            return Comment.objects.filter(post__in=accessible_posts)

        group_posts = BlogPost.objects.filter(
            author__groups__in=user.groups.all(),
            group_access__in=["Read", "Read and Edit"]
        )

        author_posts = BlogPost.objects.filter(
            author=user,
            author_access__in=["Read", "Read and Edit"]
        )

        authenticated_posts = BlogPost.objects.filter(
            authenticated_access__in=["Read", "Read and Edit"]
        )

        accessible_posts = group_posts | author_posts | authenticated_posts

        return Comment.objects.filter(post__in=accessible_posts) | Comment.objects.filter(user=user)
    
    def perform_create(self, serializer):
        """ Asigna el usuario y el post automáticamente al crear un comentario. """
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['GET'], url_path='filter_post/(?P<post_id>[^/.]+)')
    def post_comments(self, request, post_id, pk=None):
        """ Lista los comentarios de un post específico. """
        queryset = self.get_queryset()  # Apply existing queryset filter
        comment = queryset.filter(post_id=post_id)  # Filter likes given by this user

        serializer = CommentSerializer(comment, many=True)
        return Response(serializer.data)
    

    @action(detail=False, methods=['GET'], url_path='filter_user/(?P<user_id>[^/.]+)')
    def user_comments(self, request, user_id, pk=None):
        """ Lista los comentarios de un post específico. """
        queryset = self.get_queryset()  # Apply existing queryset filter
        comment = queryset.filter(user_id=user_id)  # Filter likes given by this user

        serializer = CommentSerializer(comment, many=True)
        return Response(serializer.data)

class LikeViewSet(viewsets.ModelViewSet):
    """ Vista CRUD de likes. """
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    pagination_class = LikePagination

    def get_queryset(self):
        """ Filtra los likes según los permisos del usuario sobre los posts. """
        user = self.request.user

        # Superusers and staff get all likes
        if user.is_superuser or user.is_staff:
            return Like.objects.all()

        # Unauthenticated users only see likes on publicly accessible posts
        if not user.is_authenticated:
            accessible_posts = BlogPost.objects.filter(public_access__in=["Read", "Read and Edit"])
            return Like.objects.filter(post__in=accessible_posts)

        # Users in the same group as the post author
        group_posts = BlogPost.objects.filter(
            author__groups__in=user.groups.all(),
            group_access__in=["Read", "Read and Edit"]
        )

        # Users who are the author of the post
        author_posts = BlogPost.objects.filter(
            author=user,
            author_access__in=["Read", "Read and Edit"]
        )

        # Authenticated users without group match but with general authenticated access
        authenticated_posts = BlogPost.objects.filter(
            authenticated_access__in=["Read", "Read and Edit"]
        )

        # Merge all accessible posts
        accessible_posts = group_posts | author_posts | authenticated_posts

        return Like.objects.filter(post__in=accessible_posts) | Like.objects.filter(user=user)
    
    def perform_create(self, serializer):
        """ Asigna el usuario y el post automáticamente al crear un comentario. """
        serializer.save(user=self.request.user)

    @action(detail=False, methods=['GET'], url_path='filter_post/(?P<post_id>[^/.]+)')
    def post_likes(self, request, post_id, pk=None):
        """ Lista los likes de un post específico. """
        queryset = self.get_queryset()  # Apply existing queryset filter
        likes = queryset.filter(post_id=post_id)  # Filter likes given by this user

        serializer = LikeSerializer(likes, many=True)
        return Response(serializer.data)
        
    @action(detail=False, methods=['GET'], url_path='filter_user/(?P<user_id>[^/.]+)')
    def user_likes(self, request, user_id, pk=None):
        """Lista todos los likes dados por un usuario específico, aplicando permisos."""

        queryset = self.get_queryset()  # Apply existing queryset filter
        likes = queryset.filter(user_id=user_id)  # Filter likes given by this user

        serializer = LikeSerializer(likes, many=True)
        return Response(serializer.data)
