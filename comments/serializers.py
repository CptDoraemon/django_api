from rest_framework import serializers
from comments.models import Comment
from account.serializer import AccountBaseInfoSerializer

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


class CommentBaseSerializer(serializers.ModelSerializer):
    owner = AccountBaseInfoSerializer()
    likes = serializers.IntegerField(source='liked_by.count', read_only=True)
    dislikes = serializers.IntegerField(source='disliked_by.count', read_only=True)

    class Meta:
        model = Comment
        exclude = ["is_deleted", "parent_post", "parent_comment"]


class CommentWithLoginSerializer(CommentBaseSerializer):
    is_liked = serializers.SerializerMethodField()
    is_saved = serializers.SerializerMethodField()
    is_owner = serializers.SerializerMethodField()

    def get_is_liked(self, obj):
        result = 0
        if obj.liked_by.filter(pk=self.context.get('user').pk).exists():
            result = 1
        if obj.disliked_by.filter(pk=self.context.get('user').pk).exists():
            result = -1
        return result

    def get_is_saved(self, obj):
        return obj.saved_by.filter(pk=self.context.get('user').pk).exists()

    def get_is_owner(self, obj):
        return obj.owner.pk == self.context.get('user').pk


# pass first level comments only
class NestedCommentsBaseSerializer(CommentBaseSerializer):
    sub_comments = CommentBaseSerializer(many=True)


# pass first level comments only
class NestedCommentsWithLoginSerializer(CommentWithLoginSerializer):
    sub_comments = serializers.SerializerMethodField()

    def get_sub_comments(self, obj):
        return CommentWithLoginSerializer(getattr(obj, 'sub_comments'), many=True, context=self.context).data


