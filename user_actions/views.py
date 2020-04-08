from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from response_templates.templates import success_template, error_template
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.response import Response
from user_actions.serializers import LikeUpdateSerializer, TARGET_TYPE_CHOICES
from user_actions.models import UserActions
from posts.models import Post
from comments.models import Comment
from comments.serializers import AllCommentsSerializer
from posts.serializers import AllPostsSerializer


def toggle_like(action, like_field, dislike_field, target):
    if action == 1:
        # like a target
        # cancel dislike first if applicable
        if target in dislike_field.all():
            dislike_field.remove(target)
        like_field.add(target)
    elif action == 0:
        # neutral a target
        # cancel dislike and like if applicable
        if target in dislike_field.all():
            dislike_field.remove(target)
        if target in like_field.all():
            like_field.remove(target)
    if action == -1:
        # dislike a target
        # cancel like first if applicable
        if target in like_field.all():
            like_field.remove(target)
        dislike_field.add(target)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def like_update_view(request):
    serializer = LikeUpdateSerializer(data=request.data)
    if not serializer.is_valid():
        return Response(error_template(serializer.errors), status=status.HTTP_400_BAD_REQUEST)

    user = request.user
    this_user_action = UserActions.objects.get_or_create(user=user)[0]
    target_type = serializer.validated_data['target_type']
    action = serializer.validated_data['action']
    target_id = serializer.validated_data['target_id']

    # get target comment / post
    target = None
    try:
        if target_type == TARGET_TYPE_CHOICES['comment']:
            target = Comment.objects.get(pk=target_id)
        elif target_type == TARGET_TYPE_CHOICES['post']:
            target = Post.objects.get(pk=target_id)
    except ObjectDoesNotExist:
        return Response(error_template('no such target_id'), status=status.HTTP_404_NOT_FOUND)

    # toggle like
    if target_type == TARGET_TYPE_CHOICES['comment']:
        toggle_like(
            action,
            this_user_action.liked_comments,
            this_user_action.disliked_comments,
            target
        )
    elif target_type == TARGET_TYPE_CHOICES['post']:
        toggle_like(
            action,
            this_user_action.liked_posts,
            this_user_action.disliked_posts,
            target
        )

    return Response(success_template(), status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def all_liked_view(request):
    user = request.user
    this_user_action = UserActions.objects.get_or_create(user=user)[0]

    category = request.GET.get('category')
    data = {}
    if category == 'comment':
        comments = AllCommentsSerializer(this_user_action.liked_comments, many=True).data
        data['comments'] = comments
    elif category == 'post':
        posts = AllPostsSerializer(this_user_action.liked_posts, many=True).data
        data['posts'] = posts
    else:
        comments = AllCommentsSerializer(this_user_action.liked_comments, many=True).data
        posts = AllPostsSerializer(this_user_action.liked_posts, many=True).data
        data['comments'] = comments
        data['posts'] = posts

    return Response(success_template(data=data), status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def all_disliked_view(request):
    user = request.user
    this_user_action = UserActions.objects.get_or_create(user=user)[0]

    category = request.GET.get('category')
    data = {}
    if category == 'comment':
        comments = AllCommentsSerializer(this_user_action.disliked_comments, many=True).data
        data['comments'] = comments
    elif category == 'post':
        posts = AllPostsSerializer(this_user_action.disliked_posts, many=True).data
        data['posts'] = posts
    else:
        comments = AllCommentsSerializer(this_user_action.disliked_comments, many=True).data
        posts = AllPostsSerializer(this_user_action.disliked_posts, many=True).data
        data['comments'] = comments
        data['posts'] = posts

    return Response(success_template(data=data), status=status.HTTP_200_OK)


