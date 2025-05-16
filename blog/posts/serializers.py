from rest_framework import serializers
from .models import BlogPost
from users.serializers import BasicUserSerializer
from interactions.serializers import LikeSerializer, CommentSerializer

class BasicBlogPostSerializer(serializers.ModelSerializer):
    author = BasicUserSerializer(read_only=True)  # Muestra solo el ID y el username del autor
    class Meta:
        model = BlogPost
        fields = ('id', 'username')

class BlogPostSerializer(serializers.ModelSerializer):
    author = serializers.StringRelatedField(read_only=True)  # Muestra el username en lugar del ID
    author_groups = serializers.SerializerMethodField() 
    likes_author = LikeSerializer(many=True, read_only=True, source='likes')
    Comments_author = CommentSerializer(many=True, read_only=True, source='comments')
    permission_level = serializers.SerializerMethodField()

    class Meta:
        model = BlogPost
        fields = ('id', 'title', 'content', 'excerpt', 'author', 'created_at', 'updated_at', 'author_groups',
                  'public_access', 'authenticated_access', 'group_access', 'author_access', 'likes_author', 'Comments_author', 'permission_level')
        read_only_fields = ['excerpt']  
        

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user  # Asigna automáticamente el autor
        return super().create(validated_data)
    
    def get_author_groups(self, obj):
        return [group.name for group in obj.author.groups.all()]
    
    def get_permission_level(self, obj):
        user = self.context['request'].user

        if not user or not user.is_authenticated:
            return 1 if obj.public_access == "Read" else 0  # 0 si ni siquiera puede verlo (en caso de mal filtrado)

        if user.is_superuser or user.is_staff:
            return 3

        is_group_member = user.groups.exists() and obj.author.groups.filter(
            id__in=user.groups.values_list("id", flat=True)
        ).exists()

        # Nivel 3 – Puede editar
        if (
            (obj.author == user and obj.author_access == "Read and Edit") or
            (is_group_member and obj.group_access == "Read and Edit") or
            (obj.authenticated_access == "Read and Edit")
        ):
            return 3

        # Nivel 2 – Puede interactuar (comentarios, likes)
        if (
            (obj.public_access == "Read") or
            (obj.authenticated_access in ["Read", "Read and Edit"]) or
            (obj.author == user) or
            (is_group_member and obj.group_access in ["Read", "Read and Edit"])
        ):
            return 2

        # Nivel 1 – Solo puede ver el contenido sin interacción
        return 1