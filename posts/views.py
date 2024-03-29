from django.core.exceptions import ObjectDoesNotExist
from django.utils import timezone
from math import floor
from rest_framework import status
from rest_framework.response import Response
from posts.models import Post, TAGS
from comments.models import Comment
from posts.serializers import PostCreationSerializer, AllPostsViewQueryParamSerializer, PostDetailSerializer, PostListSerializer, WithLoginPostListSerializer, WithLoginPostDetailSerializer
from comments.serializers import NestedCommentsBaseSerializer, NestedCommentsWithLoginSerializer
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from response_templates.templates import success_template, error_template
from posts.utils.process_image import validate_and_and_optimize_images, save_image, delete_image_folder
from posts.utils.sanitize_html import sanitize_html
from django.db.models import Count
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
        tag=serializer.validated_data['tag'],
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

    # update title and tag
    post.title = serializer.validated_data['title']
    post.tag = serializer.validated_data['tag']

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
    post.edited = timezone.now()

    # update last edited
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
    # helpers
    def get_page_integer(total, per_page):
        if per_page == 0:
            return 0
        floored = floor(total / per_page)
        return floored if floored == total else floored + 1

    # possible query params
    query = AllPostsViewQueryParamSerializer(data=request.query_params)
    query.is_valid(raise_exception=True)
    page = query.validated_data.get('page')
    limit = query.validated_data.get('limit')
    tag = query.validated_data.get('tag')
    sort_by = query.validated_data.get('sort_by')
    sort_order_prefix = '-' if query.validated_data.get('sort_order') == 'desc' else ''
    sort_order_string = f'{sort_order_prefix}{sort_by}'

    # get requested posts
    offset = (page - 1) * limit
    post_filter = {"is_deleted": False}
    if tag is not None:
        post_filter["tag"] = tag

    # sort by view count is used by showing popular posts
    # include pinned posts to count popular
    if sort_by != "view_count":
        post_filter["is_pinned"] = False

    all_posts = Post.objects.defer('content').filter(**post_filter).order_by(sort_order_string)[offset:offset + limit]
    total_pages = get_page_integer(Post.objects.filter(**post_filter).count(), limit)

    # serialize response
    all_posts_data = (
        PostListSerializer(all_posts, many=True).data
        if request.user.is_anonymous
        else WithLoginPostListSerializer(all_posts, many=True, context={"user": request.user}).data
    )
    response_data = {
        "posts": all_posts_data,
        "total_pages": total_pages,
        "current_page": page
    }

    return Response(success_template(data=response_data), status=status.HTTP_200_OK)


@api_view(['GET'])
def post_detail_view(request, pk):
    if not Post.objects.filter(pk=pk).exists():
        return Response(error_template('no such post'), status=status.HTTP_404_NOT_FOUND)

    post = Post.objects.get(pk=pk)
    post.view_count = post.view_count + 1
    post.save()

    data = (
        PostDetailSerializer(post).data
        if request.user.is_anonymous
        else WithLoginPostDetailSerializer(post, context={"user": request.user}).data
    )

    first_level_comments = Comment.objects.filter(parent_comment=None, parent_post=pk)
    comments_data = (
        NestedCommentsBaseSerializer(first_level_comments, many=True).data
        if request.user.is_anonymous
        else NestedCommentsWithLoginSerializer(first_level_comments, many=True, context={"user": request.user}).data
    )
    data['comments_data'] = comments_data

    return Response(success_template(data=data), status=status.HTTP_200_OK)


@api_view(['GET'])
def post_tag_list_view(request):
    tags_dict = {tag: 0 for tag in TAGS}
    tags_count = Post.objects.all().values('tag').annotate(total=Count('tag'))
    for obj in tags_count:
        tags_dict[obj['tag']] = obj['total']

    return_list = []
    for k, v in tags_dict.items():
        return_list.append({
            'tag': k,
            'count': v
        })
    return Response(success_template(data=return_list), status=status.HTTP_200_OK)

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def pin_post_view(request):
    user = request.user
    is_pinned = request.data.get('isPinned')
    post_id = request.data.get('id')

    try:
        post = Post.objects.get(pk=post_id)
    except ObjectDoesNotExist:
        return Response(error_template('not authorized'), status=status.HTTP_403_FORBIDDEN)

    if user != post.owner:
        return Response(error_template('not authorized'), status=status.HTTP_403_FORBIDDEN)

    post.is_pinned = is_pinned
    if is_pinned:
        post.pinned_date = timezone.now()
    post.save()
    response_data = {"is_pinned": is_pinned}

    return Response(success_template(data=response_data), status=status.HTTP_200_OK)

@api_view(['GET'])
def pinned_posts_view(request):


    all_posts = Post.objects.defer('content').filter(is_pinned=True).order_by('pinned_date')

    # serialize response
    all_posts_data = (
        PostListSerializer(all_posts, many=True).data
        if request.user.is_anonymous
        else WithLoginPostListSerializer(all_posts, many=True, context={"user": request.user}).data
    )
    response_data = {
        "posts": all_posts_data
    }

    return Response(success_template(data=response_data), status=status.HTTP_200_OK)
