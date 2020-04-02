from rest_framework import generics
from posts.models import Post
from posts.serializers import PostsSerializer


class AllPosts(generics.ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostsSerializer