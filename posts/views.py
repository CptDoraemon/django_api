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
from posts.utils.process_image import validate_and_and_optimize_images, save_image, delete_image_folder
from posts.utils.sanitize_html import sanitize_html
import os


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def post_creation_view(request):
    serializer = PostCreationSerializer(data=request.data)
    if not serializer.is_valid(raise_exception=True):
        return

    # validate image before save anything
    validated_optimized_images = None
    if len(request.FILES) > 0:
        validated_optimized_images = validate_and_and_optimize_images(request.FILES)

    # part save to get pk first:
    user = request.user
    content = serializer.validated_data['content']
    content = sanitize_html(content)
    post = Post(
        title=serializer.validated_data['title'],
        content=content,
        owner=user
    )
    post.save()
    post_id = post.pk

    # save image to storage
    # replace objectURLs in content with storage url
    if validated_optimized_images is not None:
        for i, file in enumerate(validated_optimized_images):
            image_url = save_image(file, post_id, i)
            filename_without_ext = os.path.splitext(file.name)[0]
            content = content.replace(filename_without_ext, image_url)
        post.content = content
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

    # validate image before save anything
    validated_optimized_images = None
    if len(request.FILES) > 0:
        validated_optimized_images = validate_and_and_optimize_images(request.FILES)

    # update title
    post.title = serializer.validated_data['title']

    # save image to storage
    # replace objectURLs in content with storage url
    content = serializer.validated_data['content']
    content = sanitize_html(content)
    if validated_optimized_images is not None:
        for i, file in enumerate(validated_optimized_images):
            image_url = save_image(file, post_id, i)
            filename_without_ext = os.path.splitext(file.name)[0]
            content = content.replace(filename_without_ext, image_url)

    # TODO: clean up deleted images in storage

    # save updated post
    post.content = content
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

    post.delete()
    delete_image_folder(post_id)

    return Response(success_template(), status=status.HTTP_200_OK)


@api_view(['GET'])
def all_posts_view(request):
    all_posts = Post.objects.filter(is_deleted=False).order_by('-created')
    all_posts_data = (
        PostBaseSerializer(all_posts, many=True).data
        if request.user.is_anonymous
        else PostWithLoginSerializer(all_posts, many=True, context={"user": request.user}).data
    )

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