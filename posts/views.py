from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.response import Response
from posts.models import Post
from posts.serializers import PostCreationSerializer, AllPostsBaseSerializer, AllPostsWithLoginSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from response_templates.templates import success_template, error_template
from comments.serializers import AllCommentsSerializer
from rest_framework_simplejwt import authentication


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
    all_posts = Post.objects.filter(is_deleted=False)
    all_posts_data = (
        AllPostsBaseSerializer(all_posts, many=True).data
        if request.user.is_anonymous
        else AllPostsWithLoginSerializer(all_posts, many=True, context={"user": request.user}).data
    )

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


# @api_view(['GET'])
# def post_detail_view(request):
