from rest_framework import serializers, fields
from posts.models import Post, TAG_CHOICES
from account.serializer import AccountBaseInfoSerializer


class PostCreationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Post
        fields = ['title', 'content', 'tag']
        # owner = serializers.ReadOnlyField(source='owner.username')


class PostSerializer(serializers.ModelSerializer):
    owner = AccountBaseInfoSerializer()
    likes = serializers.IntegerField(source='liked_by.count', read_only=True)
    dislikes = serializers.IntegerField(source='disliked_by.count', read_only=True)
    comments = serializers.IntegerField(source='comments.count', read_only=True)

    class Meta:
        model = Post


class PostDetailSerializer(PostSerializer):
    class Meta:
        model = Post
        exclude = ['is_deleted']


class PostListSerializer(PostSerializer):
    class Meta:
        model = Post
        exclude = ['is_deleted', 'content']


def with_login(BaseSerializer):
    class WithLoginSerializer(BaseSerializer):
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

    return WithLoginSerializer


WithLoginPostDetailSerializer = with_login(PostDetailSerializer)
WithLoginPostListSerializer = with_login(PostListSerializer)


class AllPostsViewQueryParamSerializer(serializers.Serializer):
    tag = fields.ChoiceField(TAG_CHOICES, default=None, allow_null=True)
    page = fields.IntegerField(min_value=0, default=1, allow_null=True)
    limit = fields.IntegerField(min_value=0, max_value=50, default=15, allow_null=True)
    sort_by = fields.ChoiceField(['created', 'view_count'], default='created', allow_null=True)
    sort_order = fields.ChoiceField(['asc', 'desc'], default='desc', allow_null=True)

