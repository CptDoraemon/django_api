from rest_framework.decorators import api_view, permission_classes
from rest_framework.permissions import IsAuthenticated
from response_templates.templates import success_template, error_template
from comments.serializers import CommentSerializer
from comments.models import Comment

# Create your views here.

@api_view(['POST'])
@permission_classes([IsAuthenticated])
def create_comment_view(request):
    serializer = CommentSerializer(data=request.data)
    if serializer.is_valid():
        user = request.user
        comment = Comment(
            content=serializer.validated_data['content'],
        )
        post.save()
        return Response(success_template(data={'post_id': post.pk}), status=status.HTTP_200_OK)
    else:
        return Response(error_template(serializer.errors), status=status.HTTP_400_BAD_REQUEST)