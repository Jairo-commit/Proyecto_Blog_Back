from django.shortcuts import render
from rest_framework import viewsets

from .models import Comment, Like
from .serializers import LikeSerializer, CommentSerializer
from .pagination import LikePagination, CommentPagination

# Create your views here.

class CommentViewSet(viewsets.ModelViewSet):
    """ Vista CRUD de comentarios. """
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    pagination_class = CommentPagination

    def perform_create(self, serializer):
        """ Asigna el usuario y el post automáticamente al crear un comentario. """
        serializer.save(user=self.request.user)

class LikeViewSet(viewsets.ModelViewSet):
    """ Vista CRUD de likes. """
    queryset = Like.objects.all()
    serializer_class = LikeSerializer
    pagination_class = LikePagination

    def perform_create(self, serializer):
        """ Asigna el usuario y el post automáticamente al crear un comentario. """
        serializer.save(user=self.request.user)




