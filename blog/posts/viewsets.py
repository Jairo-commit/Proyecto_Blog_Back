from rest_framework.decorators import action
from rest_framework.response import Response
from django.db.models import Q
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework import viewsets

from interactions.permissions import CommentPermission
from interactions.models import Like, Comment
from .models import BlogPost
from .serializers import BlogPostSerializer
from .permissions import BlogPostPermission 
from interactions.serializers import CommentSerializer
from .pagination import BlogPostPagination

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

    def get_queryset(self):
        user = self.request.user

        # Si es superusuario, devuelve todo
        if user.is_superuser or user.is_staff:
            return BlogPost.objects.all()

        # Si el usuario no está autenticado, filtra por permisos públicos
        if not user.is_authenticated:
            return BlogPost.objects.filter(public_access="Read")

        # Construcción de filtros con Q() para evitar problemas de combinación
        query = Q(public_access="Read") | Q(authenticated_access="Read") | Q(author=user)

        # Agregar filtro por grupos si hay grupos asociados
        user_groups = user.groups.all()
        if user_groups.exists():
            query |= Q(group_access="Read", author__groups__in=user_groups)

        # Construcción de filtros con Q() para evitar problemas de combinación
        query2 = Q(public_access="Read and Edit") | Q(authenticated_access="Read and Edit")

        # Agregar filtro por grupos si hay grupos asociados
        user_groups = user.groups.all()
        if user_groups.exists():
            query2 |= Q(group_access="Read and Edit", author__groups__in=user_groups)

        return BlogPost.objects.filter(query).distinct() and BlogPost.objects.filter(query2).distinct()


    def perform_create(self, serializer):
        """
        Asigna automáticamente el usuario autenticado como autor del post.
        """
        serializer.save(author=self.request.user)

    @action(detail=True, methods=['post', 'get'], permission_classes=[BlogPostPermission])
    def giving_like(self, request, pk=None):
        """
        Acción para dar o quitar like a un post.
        """
        post = get_object_or_404(BlogPost, id=pk)
        user = request.user

        # ✅ Verificar si el usuario tiene permiso de lectura sobre el post antes de permitir dar like
        if not BlogPostPermission().has_object_permission(request, self, post):
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
    
    @action(detail=True, methods=['get', 'post'], serializer_class=CommentSerializer, permission_classes=[BlogPostPermission])
    def writing_comment(self, request, pk=None):
        """
        Acción para escribir un comentario en un post.
        """
        post = get_object_or_404(BlogPost, id=pk)
        user = request.user
        comment = CommentSerializer(data=request.data)

        # ✅ Verificar si el usuario tiene permiso de lectura sobre el post antes de permitir dar like
        if not BlogPostPermission().has_object_permission(request, self, post):
            return Response({'detail': 'No tienes permiso para interactuar con este post.'}, status=status.HTTP_403_FORBIDDEN)

        if comment.is_valid():
            comment.save(user=user, post=post)
            return Response({'detail': 'Comentario agregado correctamente.'}, status=status.HTTP_200_OK)
        
        return Response(comment.errors, status=status.HTTP_400_BAD_REQUEST)
    
    @action(detail=True, 
            methods=['GET', 'DELETE', 'PATCH'], 
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
        if request.method == 'PATCH':
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
    
    @action(
    detail=True,
    methods=['GET', 'POST'],  # ✅ Only allow GET requests
    url_path='comments',  # ✅ This makes the endpoint /api/post/{post_id}/comments/
    permission_classes=[CommentPermission],
    serializer_class=CommentSerializer
)
    def list_comments(self, request, pk=None):
        """
        GET: Obtener todos los comentarios de un post.
        POST: Agregar un comentario al post si el usuario tiene permisos.
        """
        post = self.get_object()  # Obtiene el post

        # ✅ Manejo de GET: Retornar los comentarios existentes
        if request.method == 'GET':
            comments = Comment.objects.filter(post=post)
            serializer = CommentSerializer(comments, many=True)
            return Response(serializer.data, status=status.HTTP_200_OK)

        # ✅ Manejo de POST: Crear un nuevo comentario
        if request.method == 'POST':

            serializer = CommentSerializer(data=request.data)
            if serializer.is_valid():
                serializer.save(user=request.user, post=post)  # Guarda el comentario con el usuario y post
                return Response(serializer.data, status=status.HTTP_201_CREATED)
            
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

