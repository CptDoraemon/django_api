from rest_framework import status
from rest_framework.response import Response
from rest_framework.decorators import api_view, permission_classes
from account.serializer import RegistrationSerializer, ResetPasswordSerializer, UpdateAvatarSerializer
from response_templates.templates import success_template, error_template
from django.contrib.auth import authenticate
from rest_framework.permissions import IsAuthenticated
from rest_framework_simplejwt.tokens import RefreshToken
from storages.backends.s3boto3 import S3Boto3Storage
import os
from urllib.parse import urlparse
import time
from numpy import base_repr
from account.utils.resize_image import resize_image


@api_view(['POST'])
def registration_view(request):
    serializer = RegistrationSerializer(data=request.data)
    if not serializer.is_valid(raise_exception=True):
        return

    user = serializer.save()
    refresh = RefreshToken.for_user(user)
    data = {
        'refresh': str(refresh),
        'access': str(refresh.access_token),
        'username': user.username
    }
    return Response(success_template(data=data), status=status.HTTP_201_CREATED)


# @api_view(['POST'])
# def login_view(request):
#     serializer = LoginSerializer(data=request.data)
#     # check input validation
#     if not serializer.is_valid(raise_exception=True):
#         return
#
#     # validated
#     email = serializer.validated_data['email']
#     password = serializer.validated_data['password']
#     user_of_provided_email = Account.objects.filter(email=email)
#
#     # check if email exists
#     if not user_of_provided_email.exists():
#         return Response(error_template('No active account found with the email provided'), status=status.HTTP_400_BAD_REQUEST)
#
#     # try log in
#     user = authenticate(request, email=email, password=password)
#     if user is None:
#         return Response(error_template('credential error'), status=status.HTTP_400_BAD_REQUEST)
#     else:
#         login(request, user)
#         csrf_token = get_token(request)
#         data = {
#             'username': user.username,
#             'csrf_token': csrf_token
#         }
#         return Response(success_template(data=data), status=status.HTTP_200_OK)


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def verify_session_view(request):
    return Response(success_template(), status=status.HTTP_200_OK)


# @api_view(['POST'])
# @permission_classes([IsAuthenticated])
# def logout_view(request):
#     logout(request)
#     return Response(success_template(), status=status.HTTP_200_OK)


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


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def update_avatar_view(request):
    serializer = UpdateAvatarSerializer(data=request.data)

    if not serializer.is_valid(raise_exception=True):
        return

    file = serializer.validated_data['image']

    # resize, optimize and check size
    file = resize_image(file, file.name, 200, 200)
    if file.size > 5 * 1024 * 1024:
        return Response(error_template('Image file too big'), status=status.HTTP_200_OK)

    # vars
    user = request.user
    file_directory_within_bucket = 'avatars/'
    old_avatar_url = user.avatar_url
    media_storage = S3Boto3Storage()

    # delete old avatar if exists
    if len(old_avatar_url) > 0:
        url = urlparse(old_avatar_url)
        old_avatar_filename = os.path.basename(url.path)
        old_avatar_file_path_within_bucket = os.path.join(
            file_directory_within_bucket,
            old_avatar_filename
        )
        if media_storage.exists(old_avatar_file_path_within_bucket):
            media_storage.delete(old_avatar_file_path_within_bucket)

    # save new avatar
    random_string = base_repr(int(time.time()*1000), 36)
    file_name = 'avatar_' + user.username + '_' + random_string + os.path.splitext(file.name)[1]
    file_path_within_bucket = os.path.join(
        file_directory_within_bucket,
        file_name
    )
    media_storage.save(file_path_within_bucket, file)
    file_url = media_storage.url(file_path_within_bucket)

    # update user obj
    user.avatar_url = file_url
    user.save()

    return Response(success_template(), status=status.HTTP_200_OK)
