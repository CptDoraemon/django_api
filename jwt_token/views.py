from rest_framework_simplejwt.serializers import TokenObtainPairSerializer
from rest_framework_simplejwt.views import TokenViewBase
from rest_framework_simplejwt.exceptions import InvalidToken, TokenError
from rest_framework.response import Response
from response_templates.templates import success_template
from rest_framework import status


class CustomizedTokenViewBase(TokenViewBase):

    def post(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)

        try:
            serializer.is_valid(raise_exception=True)
        except TokenError as e:
            raise InvalidToken(e.args[0])

        data = success_template(data=serializer.validated_data)
        return Response(data, status=status.HTTP_200_OK)


# get token pair
class CustomizedTokenObtainPairView(CustomizedTokenViewBase):
    serializer_class = TokenObtainPairSerializer


# refresh tokens
class CustomizedTokenRefreshView(CustomizedTokenViewBase):
    serializer_class = TokenObtainPairSerializer

