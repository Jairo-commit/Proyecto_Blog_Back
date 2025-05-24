from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework import viewsets

from interactions.permissions import CommentPermission, InteractionPermission
from interactions.models import Like, Comment
from .models import BlogPost
from .serializers import BlogPostSerializer
from .permissions import BlogPostPermission
from interactions.serializers import CommentSerializer, LikeSerializer
from .pagination import BlogPostPagination
from interactions.pagination import LikePagination, CommentPagination  


class BlogPostViewSet(viewsets.ModelViewSet):
    """
    ViewSet para manejar los posts del blog.
    - Usa permisos personalizados basados en el grupo del autor.
    - Permite listar, ver, crear, actualizar y eliminar posts según permisos.
    """
    queryset = BlogPost.objects.all()
    serializer_class = BlogPostSerializer
    permission_classes = [BlogPostPermission]
    pagination_class = BlogPostPagination

    def create(self, request, *args, **kwargs):
        if not self.request.user.is_authenticated:
            return Response({'detail': 'Debes loguearte primero para crear post'}, status=status.HTTP_400_BAD_REQUEST)
        return super().create(request, *args, **kwargs)

    def get_queryset(self):
        user = self.request.user

        if user.is_superuser or user.is_staff:
            return BlogPost.objects.all().order_by("-created_at")

        if not user.is_authenticated:
            return BlogPost.objects.filter(public_access="Read").order_by("-created_at")

        # Base query: Public access, authenticated access, or user's own posts
        query = Q(authenticated_access__in=["Read", "Read and Edit"]) | Q(author=user)

        user_groups = list(user.groups.all())  # Convert to a list to avoid queryset issues
        if user_groups:
            query |= Q(group_access__in=["Read", "Read and Edit"], author__groups__in=user_groups)

        return BlogPost.objects.filter(query).distinct().order_by('-created_at')

    def perform_create(self, serializer):
        """
        Asigna automáticamente el usuario autenticado como autor del post.
        """
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post', 'get'], permission_classes=[InteractionPermission])
    def giving_like(self, request, pk=None):
        """
        Acción para dar o quitar like a un post.
        """
        post = get_object_or_404(BlogPost, id=pk)
        user = request.user

        # ✅ Verificar si el usuario tiene permiso de lectura sobre el post antes de permitir dar like
        if not InteractionPermission().has_object_permission(request, self, post):
            return Response({'detail': 'No tienes permiso para interactuar con este post.'}, status=status.HTTP_403_FORBIDDEN)

        if request.method == 'GET':  # Si es GET, solo mostrar si el usuario ha dado like
            liked = Like.objects.filter(post=post, user=user).exists()
            return Response({'liked': liked, 'like_count': Like.objects.filter(post=post).count()}, status=status.HTTP_200_OK)

        # ✅ Corrección: Crear/eliminar un Like en lugar de modificar `post.likes`
        like, created = Like.objects.get_or_create(user=user, post=post)

        if not created:  
            like.delete()
            return Response({'detail': 'Like eliminado correctamente.', 'like_count': Like.objects.filter(post=post).count()}, status=status.HTTP_200_OK)

        return Response({'detail': 'Like agregado correctamente.', 'like_count': Like.objects.filter(post=post).count()}, status=status.HTTP_200_OK)
    
    @action(
        detail=True,
        methods=['GET'],
        url_path='comments',
        permission_classes=[CommentPermission],
        serializer_class=CommentSerializer
    )
    def list_comments(self, request, pk=None):
        """
        GET: Obtener todos los comentarios de un post.
        """
        post = self.get_object()
        comments = Comment.objects.filter(post=post).order_by("created_at")

        paginator = CommentPagination()
        page = paginator.paginate_queryset(comments, request, view=self)

        if page is not None:
            serializer = CommentSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = CommentSerializer(comments, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)

    @action(
        detail=True,
        methods=['POST'],
        url_path='add-comment',  # 🔹 Nuevo endpoint: /api/post/{post_id}/add-comment/
        permission_classes=[InteractionPermission],
        serializer_class=CommentSerializer
    )    
    def add_comment(self, request, pk=None):
        """
        POST: Agregar un comentario al post si el usuario tiene permisos.
        """
        post = self.get_object()  # Obtiene el post

        if request.user.is_anonymous:
            return Response({"error": "Authentication required to comment."}, status=status.HTTP_403_FORBIDDEN)

        serializer = CommentSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(user=request.user, post=post)  # Guarda el comentario con el usuario y post
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)     

    @action(
        detail=True,
        methods=['GET'], 
        url_path='likes', 
        serializer_class=LikeSerializer
    )
    def list_likes(self, request, pk=None):
        """
        GET: Obtener todos los likes de un post.
        """
        post = self.get_object()
        likes = Like.objects.filter(post=post).order_by("id")

        paginator = LikePagination()
        page = paginator.paginate_queryset(likes, request, view=self)

        if page is not None:
            serializer = LikeSerializer(page, many=True)
            return paginator.get_paginated_response(serializer.data)

        serializer = LikeSerializer(likes, many=True)
        return Response(serializer.data, status=status.HTTP_200_OK)
        
    
    @action(detail=True, 
            methods=['GET', 'DELETE'], 
            url_path='likes/(?P<like_pk>[^/.]+)',
            permission_classes=[CommentPermission],
            serializer_class=LikeSerializer) 
    def get_like(self, request, pk=None, like_pk=None):
        """
        Obtiene un comentario específico de un post.
        """
        post = self.get_object()  # Obtiene el post y aplica permisos

        like = get_object_or_404(Like, pk=like_pk, post=post)

        if request.method == 'DELETE':
            if like.user != request.user and not request.user.is_superuser:
                return Response({'detail': 'No tienes permiso para eliminar este like.'}, status=status.HTTP_403_FORBIDDEN)
            like.delete()
            return Response({'detail': 'like eliminado correctamente.'}, status=status.HTTP_204_NO_CONTENT)

        serializer = LikeSerializer(like) #Default: Handle GET
        
        return Response(serializer.data, status=status.HTTP_200_OK)
    
    @action(detail=True, 
            methods=['GET', 'DELETE', 'PATCH', 'PUT'], 
            url_path='comments/(?P<comment_pk>[^/.]+)', # tambien se puede usar esta esta expresión 'comments/(?P<comment_pk>\\d+) o lo de Danilo' int:<variable>
            permission_classes=[CommentPermission],
            serializer_class=CommentSerializer) 
    def get_comment(self, request, pk=None, comment_pk=None):
        """
        Obtiene un comentario específico de un post.
        - **GET /api/posts/{post_id}/comments/{comment_pk}/** → Devuelve un solo comentario específico de un post.
        """
        post = self.get_object()  # Obtiene el post y aplica permisos

        # Buscar el comentario específico dentro del post
        comment = get_object_or_404(Comment, pk=comment_pk, post=post)

        if request.method == 'DELETE':
            if comment.user != request.user and not request.user.is_superuser:
                return Response({'detail': 'No tienes permiso para eliminar este comentario.'}, status=status.HTTP_403_FORBIDDEN)
            comment.delete()
            return Response({'detail': 'Comentario eliminado correctamente.'}, status=status.HTTP_204_NO_CONTENT)
        
        # ✅ Handle PUT (Full Update) and PATCH (Partial Update)
        if request.method in ['PATCH', 'PUT']:
            if comment.user != request.user and not request.user.is_superuser:
                return Response({'detail': 'You do not have permission to edit this comment.'}, status=status.HTTP_403_FORBIDDEN)
            
            serializer = CommentSerializer(comment, data=request.data, partial=(request.method == 'PATCH'))
            if serializer.is_valid():
                serializer.save()
                return Response(serializer.data, status=status.HTTP_200_OK)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        # Serializar el comentario
        serializer = CommentSerializer(comment) #Default: Handle GET
        
        return Response(serializer.data, status=status.HTTP_200_OK)