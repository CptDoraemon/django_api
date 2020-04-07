from rest_framework import serializers
from comments.models import Comment


class CommentCreationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['content', 'parent_post', 'parent_comment']


class CommentEditSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = ['content']


class AllCommentsSerializer(serializers.ModelSerializer):
    class Meta:
        model = Comment
        fields = "__all__"