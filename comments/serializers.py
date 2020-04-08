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


##


class _CommentBaseSerializer(serializers.ModelSerializer):
    likes = serializers.IntegerField(source='liked_by.count', read_only=True)
    dislikes = serializers.IntegerField(source='disliked_by.count', read_only=True)

    class Meta:
        model = Comment
        exclude = ["is_deleted", "parent_post", "parent_comment"]


class _CommentWithLoginSerializer(_CommentBaseSerializer):
    is_liked = serializers.SerializerMethodField()
    is_saved = serializers.SerializerMethodField()

    def get_is_liked(self, obj):
        result = 0
        if obj.liked_by.filter(pk=self.context.get('user').pk).exists():
            result = 1
        if obj.disliked_by.filter(pk=self.context.get('user').pk).exists():
            result = -1
        return result

    def get_is_saved(self, obj):
        return obj.saved_by.filter(pk=self.context.get('user').pk).exists()


# pass first level comments only
class NestedCommentsBaseSerializer(_CommentBaseSerializer):
    sub_comments = _CommentBaseSerializer(many=True)


# pass first level comments only
class NestedCommentsWithLoginSerializer(_CommentWithLoginSerializer):
    sub_comments = serializers.SerializerMethodField()

    def get_sub_comments(self, obj):
        return _CommentWithLoginSerializer(getattr(obj, 'sub_comments'), many=True, context=self.context).data


