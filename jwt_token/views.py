from rest_framework_simplejwt.serializers import TokenObtainPairSerializer, TokenRefreshSerializer
from rest_framework_simplejwt.views import TokenViewBase
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework.response import Response
from response_templates.templates import success_template
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication


# get token pair
class _CustomizedTokenViewBaseWithUserInfo(TokenViewBase):

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        data = serializer.validated_data
        data['username'] = serializer.user.username
        return Response(success_template(data=data), status=status.HTTP_200_OK)


class CustomizedTokenObtainPairView(_CustomizedTokenViewBaseWithUserInfo):
    serializer_class = TokenObtainPairSerializer


# refresh tokens
class _CustomizedTokenViewBase(TokenViewBase):

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        return Response(success_template(data=serializer.validated_data), status=status.HTTP_200_OK)


class CustomizedTokenRefreshView(_CustomizedTokenViewBase):
    serializer_class = TokenRefreshSerializer

