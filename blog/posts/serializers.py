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
    likes_author = LikeSerializer(many=True, read_only=True, source='likes')
    Comments_author = CommentSerializer(many=True, read_only=True, source='comments')

    class Meta:
        model = BlogPost
        fields = ('id', 'title', 'content', 'excerpt', 'author', 'created_at', 'updated_at', 
                  'public_access', 'authenticated_access', 'group_access', 'author_access', 'likes_author', 'Comments_author')
        read_only_fields = ['excerpt']
        

    def create(self, validated_data):
        validated_data['author'] = self.context['request'].user  # Asigna automáticamente el autor
        return super().create(validated_data)
    