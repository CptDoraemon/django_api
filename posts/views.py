from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.response import Response
from posts.models import Post
from posts.serializers import PostCreationSerializer, AllPostsListSerializer
from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from response_templates.templates import success_template, error_template


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def post_creation_view(request):
    serializer = PostCreationSerializer(data=request.data)
    if serializer.is_valid():
        user = request.user
        post = Post(
            title=serializer.validated_data['title'],
            content=serializer.validated_data['content'],
            owner=user
        )
        post.save()
        return Response(success_template(data={'post_id': post.pk}), status=status.HTTP_200_OK)
    else:
        return Response(error_template(serializer.errors), status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def post_edit_view(request, post_id):
    serializer = PostCreationSerializer(data=request.data)
    if serializer.is_valid():
        user = request.user
        try:
            post = Post.objects.get(pk=post_id)
        except ObjectDoesNotExist:
            return Response(error_template('not authorized'), status=status.HTTP_403_FORBIDDEN)

        if user != post.owner:
            return Response(error_template('not authorized'), status=status.HTTP_403_FORBIDDEN)

        post.title = serializer.validated_data['title']
        post.content = serializer.validated_data['content']
        post.save()
        return Response(success_template(data={'post_id': post.pk}), status=status.HTTP_200_OK)
    else:
        return Response(error_template(serializer.errors), status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def post_deletion_view(request, post_id):
    user = request.user
    try:
        post = Post.objects.get(pk=post_id)
    except ObjectDoesNotExist:
        return Response(error_template('not authorized'), status=status.HTTP_403_FORBIDDEN)

    if user != post.owner:
        return Response(error_template('not authorized'), status=status.HTTP_403_FORBIDDEN)

    post.is_deleted = True
    post.save()
    return Response(success_template(), status=status.HTTP_200_OK)


class AllPostsView(generics.ListAPIView):
    queryset = Post.objects.all()
    serializer_class = AllPostsListSerializer


