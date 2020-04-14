from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.response import Response
from posts.models import Post
from comments.models import Comment
from posts.serializers import PostCreationSerializer, PostBaseSerializer, PostWithLoginSerializer
from comments.serializers import NestedCommentsBaseSerializer, NestedCommentsWithLoginSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from response_templates.templates import success_template, error_template


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def post_creation_view(request):
    serializer = PostCreationSerializer(data=request.data)
    if not serializer.is_valid(raise_exception=True):
        return

    user = request.user
    post = Post(
        title=serializer.validated_data['title'],
        content=serializer.validated_data['content'],
        owner=user
    )
    post.save()
    return Response(success_template(data={'post_id': post.pk}), status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def post_edit_view(request, post_id):
    serializer = PostCreationSerializer(data=request.data)
    if not serializer.is_valid(raise_exception=True):
        return

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
    all_posts = Post.objects.filter(is_deleted=False).order_by('-created')
    all_posts_data = (
        PostBaseSerializer(all_posts, many=True).data
        if request.user.is_anonymous
        else PostWithLoginSerializer(all_posts, many=True, context={"user": request.user}).data
    )

    print(all_posts_data)
    print(success_template(data=all_posts_data))

    # for post in all_posts:
    #     # get all comments for this post
    #     comments = post.comment_set.filter(parent_comment=None).order_by('created')
    #     post_data = AllPostsSerializer(post).data
    #
    #     comments_data = []
    #     # get sub comments for this comment
    #     for comment in comments:
    #         sub_comments = comment.comment_set.all().order_by('created')
    #         comment_data = AllCommentsSerializer(comment).data
    #         comment_data['comments'] = []
    #         sub_comments_data = AllCommentsSerializer(sub_comments, many=True).data
    #         comment_data['comments'].append(sub_comments_data)
    #         comments_data.append(comment_data)
    #
    #     post_data['comments'] = comments_data
    #     all_posts_data.append(post_data)

    return Response(success_template(data=all_posts_data), status=status.HTTP_200_OK)


@api_view(['GET'])
def post_detail_view(request, pk):
    if not Post.objects.filter(pk=pk).exists():
        return Response(error_template('no such post'), status=status.HTTP_404_NOT_FOUND)

    post = Post.objects.get(pk=pk)
    data = (
        PostBaseSerializer(post).data
        if request.user.is_anonymous
        else PostWithLoginSerializer(post, context={"user": request.user}).data
    )

    first_level_comments = Comment.objects.filter(parent_comment=None, parent_post=pk)
    comments_data = (
        NestedCommentsBaseSerializer(first_level_comments, many=True).data
        if request.user.is_anonymous
        else NestedCommentsWithLoginSerializer(first_level_comments, many=True, context={"user": request.user}).data
    )
    data['comments_data'] = comments_data

    return Response(success_template(data=data), status=status.HTTP_200_OK)