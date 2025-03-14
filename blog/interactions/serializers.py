from rest_framework import serializers
from .models import Like, Comment


class LikeSerializer(serializers.ModelSerializer):
    user = serializers.StringRelatedField(read_only=True)
    post = serializers.StringRelatedField(read_only=True)
    post_id = serializers.IntegerField(source='post.id', read_only=True)

    class Meta:
        model = Like
        fields = ['id','post','post_id','user']


class CommentSerializer(serializers.ModelSerializer):
    id = serializers.ReadOnlyField()
    user = serializers.StringRelatedField(read_only=True)
    post = serializers.StringRelatedField(read_only=True)
    post_id = serializers.IntegerField(source='post.id', read_only=True)

    class Meta:
        model = Comment
        fields = ['id', 'user', 'post','post_id','content', 'created_at']