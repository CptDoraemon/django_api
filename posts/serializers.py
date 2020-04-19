from rest_framework import serializers
from posts.models import Post
from account.serializer import AccountBaseInfoSerializer


class PostCreationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['title', 'content']
        # owner = serializers.ReadOnlyField(source='owner.username')


class PostBaseSerializer(serializers.ModelSerializer):
    owner = AccountBaseInfoSerializer()
    likes = serializers.IntegerField(source='liked_by.count', read_only=True)
    dislikes = serializers.IntegerField(source='disliked_by.count', read_only=True)
    comments = serializers.IntegerField(source='comments.count', read_only=True)

    class Meta:
        model = Post
        fields = "__all__"


class PostWithLoginSerializer(PostBaseSerializer):
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


class PostDetailBaseSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = "__all__"


class ImageSerializer(serializers.Serializer):

    image = serializers.ImageField(allow_empty_file=False)
