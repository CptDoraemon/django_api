from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from account.serializer import RegistrationSerializer, LoginSerializer, ResetPasswordSerializer
from response_templates.templates import success_template, error_template
from django.contrib.auth import authenticate, login, logout
from rest_framework.permissions import IsAuthenticated
from account.models import Account
from django.middleware.csrf import get_token


@api_view(['POST'])
def registration_view(request):
    serializer = RegistrationSerializer(data=request.data)
    if serializer.is_valid():
        serializer.save()
        return Response(success_template(), status=status.HTTP_201_CREATED)
    else:
        return Response(error_template(serializer.errors), status=status.HTTP_400_BAD_REQUEST)


@api_view(['POST'])
def login_view(request):
    serializer = LoginSerializer(data=request.data)
    # check input validation
    if not serializer.is_valid(raise_exception=True):
        return

    # validated
    email = serializer.validated_data['email']
    password = serializer.validated_data['password']
    user_of_provided_email = Account.objects.filter(email=email)

    # check if email exists
    if not user_of_provided_email.exists():
        return Response(error_template('No active account found with the email provided'), status=status.HTTP_400_BAD_REQUEST)

    # try log in
    user = authenticate(request, email=email, password=password)
    if user is None:
        return Response(error_template('credential error'), status=status.HTTP_400_BAD_REQUEST)
    else:
        login(request, user)
        csrf_token = get_token(request)
        data = {
            'username': user.username,
            'csrf_token': csrf_token
        }
        return Response(success_template(data=data), status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_session_view(request):
    return Response(success_template(), status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    logout(request)
    return Response(success_template(), status=status.HTTP_200_OK)


@api_view(['POST'])
def reset_password_view(request):
    serializer = ResetPasswordSerializer(data=request.data)
    if serializer.is_valid():
        data = serializer.validated_data

        if data['new_password'] != data['confirm_new_password']:
            return Response(error_template('new passwords do not match'), status=status.HTTP_400_BAD_REQUEST)

        user = authenticate(request, email=data['email'], password=data['old_password'])
        if user is not None:
            user.set_password(data['new_password'])
            user.save()
            return Response(success_template(), status=status.HTTP_200_OK)

        else:
            return Response(error_template('credential error'), status=status.HTTP_400_BAD_REQUEST)

    else:
        return Response(error_template(serializer.errors), status=status.HTTP_400_BAD_REQUEST)


