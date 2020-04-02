from rest_framework import serializers
from posts.models import Post


class PostsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['title', 'content']
        # owner = serializers.ReadOnlyField(source='owner.username')