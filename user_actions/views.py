from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from response_templates.templates import success_template, error_template
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.response import Response
from user_actions.serializers import LikeUpdateSerializer, SaveUpdateSerializer, TARGET_TYPE_CHOICES
from user_actions.models import UserActions
from posts.models import Post
from comments.models import Comment
from comments.serializers import AllCommentsSerializer, CommentWithLoginSerializer
from posts.serializers import PostDetailBaseSerializer, PostWithLoginSerializer


def _toggle_like(action, user_action_instance, target, target_type):
    like_field = user_action_instance.liked_comments
    dislike_field = user_action_instance.disliked_comments
    if target_type == TARGET_TYPE_CHOICES['post']:
        like_field = user_action_instance.liked_posts
        dislike_field = user_action_instance.disliked_posts

    if action == 1:
        # like a target
        # cancel dislike first if applicable
        if target in dislike_field.all():
            dislike_field.remove(target)
        like_field.add(target)
    elif action == 0:
        # neutralize a target
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
    return _update_generic_view(request, LikeUpdateSerializer, _toggle_like)


def _toggle_save(action, user_action_instance, target, target_type):
    saved_field = user_action_instance.saved_comments
    if target_type == TARGET_TYPE_CHOICES['post']:
        saved_field = user_action_instance.saved_posts

    if action == 1:
        # save a target
        # cancel dislike first if applicable
        saved_field.add(target)
    elif action == 0:
        # neutralize a target
        # cancel saved if applicable
        if target in saved_field.all():
            saved_field.remove(target)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def save_update_view(request):
    return _update_generic_view(request, SaveUpdateSerializer, _toggle_save)


def _update_generic_view(request, serializer, toggle_handler):
    serialized = serializer(data=request.data)
    if not serialized.is_valid(raise_exception=True):
        return

    user = request.user
    this_user_action = UserActions.objects.get_or_create(user=user)[0]
    target_type = serialized.validated_data['target_type']
    action = serialized.validated_data['action']
    target_id = serialized.validated_data['target_id']

    # get target comment / post
    target = None
    try:
        if target_type == TARGET_TYPE_CHOICES['comment']:
            target = Comment.objects.get(pk=target_id)
        elif target_type == TARGET_TYPE_CHOICES['post']:
            target = Post.objects.get(pk=target_id)
    except ObjectDoesNotExist:
        return Response(error_template('no such target_id'), status=status.HTTP_404_NOT_FOUND)

    # do toggle
    toggle_handler(action, this_user_action, target, target_type)

    # return the updated target data
    target_serializer = None
    if target_type == TARGET_TYPE_CHOICES['comment']:
        target_serializer = CommentWithLoginSerializer(target, context={"user": request.user})
    elif target_type == TARGET_TYPE_CHOICES['post']:
        target_serializer = PostWithLoginSerializer(target, context={"user": request.user})

    return Response(success_template(data=target_serializer.data), status=status.HTTP_200_OK)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def all_liked_view(request):
    return _all_generic_view(
        request,
        'liked_comments',
        'liked_posts'
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def all_disliked_view(request):
    return _all_generic_view(
        request,
        'disliked_comments',
        'disliked_posts'
    )


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def all_saved_view(request):
    return _all_generic_view(
        request,
        'saved_comments',
        'saved_posts'
    )


def _all_generic_view(request, comment_field_string, post_field_string):
    user = request.user
    this_user_action = UserActions.objects.get_or_create(user=user)[0]

    category = request.GET.get('category')
    data = {}
    if category == 'comment':
        comments = AllCommentsSerializer(getattr(this_user_action, comment_field_string), many=True).data
        data['comments'] = comments
    elif category == 'post':
        posts = PostDetailBaseSerializer(getattr(this_user_action, post_field_string), many=True).data
        data['posts'] = posts
    else:
        comments = AllCommentsSerializer(getattr(this_user_action, comment_field_string), many=True).data
        posts = PostDetailBaseSerializer(getattr(this_user_action, post_field_string), many=True).data
        data['comments'] = comments
        data['posts'] = posts

    return Response(success_template(data=data), status=status.HTTP_200_OK)


