from rest_framework import serializers
from posts.models import Post


class PostCreationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['title', 'content']
        # owner = serializers.ReadOnlyField(source='owner.username')


class AllPostsListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = "__all__"

