from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view
from account.serializer import AccountSerializer
from response_templates.templates import success_template, error_template


@api_view(['POST'])
def registration_view(request):
    serializer = AccountSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(success_template(), status=status.HTTP_201_CREATED)
    else:
        return Response(error_template(serializer.errors), status=status.HTTP_400_BAD_REQUEST)