from rest_framework import serializers
from .models import Like, Comment


class LikeSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Like
        fields = ['id','user']


class CommentSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    user = serializers.StringRelatedField(read_only=True)
    post = serializers.StringRelatedField(read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'user', 'post','content', 'created_at']