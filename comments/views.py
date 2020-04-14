from comments.serializers import CommentCreationSerializer, CommentEditSerializer, AllCommentsSerializer
from comments.models import Comment
from django.core.exceptions import ObjectDoesNotExist
from rest_framework import status
from rest_framework.response import Response
from rest_framework import generics
from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from response_templates.templates import success_template, error_template
from django.utils import timezone


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def comment_creation_view(request):
    serializer = CommentCreationSerializer(data=request.data)
    if not serializer.is_valid(raise_exception=True):
        return

    user = request.user
    parent_comment = serializer.validated_data['parent_comment'] if 'parent_comment' in serializer.validated_data else None
    comment = Comment(
        content=serializer.validated_data['content'],
        owner=user,
        parent_post=serializer.validated_data['parent_post'],
        parent_comment=parent_comment,
    )
    comment.save()
    return Response(success_template(data={'parent_post_id': comment.parent_post.pk}), status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def comment_edit_view(request, comment_id):
    serializer = CommentEditSerializer(data=request.data)

    if not serializer.is_valid(raise_exception=True):
        return

    user = request.user
    try:
        comment = Comment.objects.get(pk=comment_id)
    except ObjectDoesNotExist:
        return Response(error_template('no such comment'), status=status.HTTP_400_BAD_REQUEST)

    if user != comment.owner:
        return Response(error_template('not authorized'), status=status.HTTP_403_FORBIDDEN)

    comment.content = serializer.validated_data['content']
    comment.edited = timezone.now()
    comment.save()
    return Response(success_template(data={'post_id': comment.parent_post.pk}), status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def comment_deletion_view(request, comment_id):
    user = request.user
    try:
        comment = Comment.objects.get(pk=comment_id)
    except ObjectDoesNotExist:
        return Response(error_template('no such comment'), status=status.HTTP_403_FORBIDDEN)

    if user != comment.owner:
        return Response(error_template('not authorized'), status=status.HTTP_403_FORBIDDEN)

    comment.is_deleted = True
    comment.save()
    return Response(success_template(), status=status.HTTP_200_OK)


class AllCommentsView(generics.ListAPIView):
    queryset = Comment.objects.all()
    serializer_class = AllCommentsSerializer


