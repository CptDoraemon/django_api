from rest_framework import status
from rest_framework.response import Response
from posts.models import Post
from account.models import Account
from posts.serializers import PostsSerializer
from rest_framework import generics
from rest_framework.mixins import CreateModelMixin, RetrieveModelMixin, UpdateModelMixin, DestroyModelMixin
from rest_framework.views import APIView


class AllPostsView(generics.ListAPIView):
    queryset = Post.objects.all()
    serializer_class = PostsSerializer
    # permission_classes = [IsAdminUser]


class CreatePostView(generics.CreateAPIView):
    # queryset = Post.objects.all()
    serializer_class = PostsSerializer


class EditPostView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostsSerializer
    lookup_fields = ['pk']
    # lookup_url_kwarg = ['pk']


# @api_view(['GET'])
# def detail_post_view(request, slug):
#     try:
#         post = Post.objects.get(slug=slug)
#     except Post.DoesNotExist:
#         return Response(status=status.HTTP_404_NOT_FOUND)
#
#     serializer = PostsSerializer(post)
#     return Response(serializer.data)
#
#
# @api_view(['POST'])
# def update_post_view(request, slug):
#     try:
#         post = Post.objects.get(slug=slug)
#     except Post.DoesNotExist:
#         return Response(status=status.HTTP_404_NOT_FOUND)
#
#     serializer = PostsSerializer(post, data=request.data)
#     data = {}
#     if serializer.is_valid():
#         serializer.save()
#         data["success"] = "update successful"
#         return Response(data=data)
#     return Response(serializer.data, status=status.HTTP_400_BAD_REQUEST)
#
#
# @api_view(['DELETE'])
# def delete_post_view(request, slug):
#     try:
#         post = Post.objects.get(slug=slug)
#     except Post.DoesNotExist:
#         return Response(status=status.HTTP_404_NOT_FOUND)
#
#     operation = post.delete(slug=slug)
#     data = {}
#     if operation:
#         data["success"] = "delete successful"
#     else:
#         data["failure"] = "delete failed"
#     return Response(data=data)
#
#
# @api_view(['PUT'])
# def create_post_view(request):
#     account = Account.objects.get(pk=1)
#     post = Post(owner=account)
#
#     serializer = PostsSerializer(post, data=request.data)
#     data = {}
#     if serializer.is_valid():
#         serializer.save()
#         return Response(serializer.data, status=status.HTTP_201_CREATED)
#     return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)