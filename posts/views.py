from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.response import Response
from posts.models import Post
from posts.serializers import PostCreationSerializer, AllPostsSerializer
from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from response_templates.templates import success_template, error_template
from comments.models import Comment
from comments.serializers import AllCommentsSerializer


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


@api_view(['GET'])
def all_posts_view(request):
    all_posts = Post.objects.all()
    all_posts_serializer = AllPostsSerializer(all_posts, many=True)
    data = all_posts_serializer.data
    for post in data:
        # get all comments for this post
        all_comments = Comment.objects.filter(parent_post=post['id'])
        all_comments_serializer = AllCommentsSerializer(all_comments, many=True)
        comments = all_comments_serializer.data

        # filter out first level comments
        first_level_comments = {}
        for comment in comments:
            if comment['parent_comment'] is None:
                comment['comments'] = []
                first_level_comments[comment['id']] = comment

        # append second level comments to first level comments
        for comment in comments:
            parent_comment_id = comment['parent_comment']
            if parent_comment_id is not None:
                if parent_comment_id in first_level_comments:
                    first_level_comments[parent_comment_id]['comments'].append(comment)

        first_level_comments = list(first_level_comments.values())

        # sort comments by create date
        # for first_level_comment in first_level_comments:
        #     first_level_comment['comments'] = first_level_comment['comments'].sort(key=lambda obj: obj['created'])
        # first_level_comments.sort(key=lambda obj: obj['created'])

        post['comments'] = first_level_comments

    return Response(success_template(data), status=status.HTTP_200_OK)


