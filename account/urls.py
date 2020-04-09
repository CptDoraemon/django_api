from django.urls import path
from account import views
from rest_framework_simplejwt.views import (
    # TokenObtainPairView,
    TokenRefreshView,
)
from jwt_token.views import CustomizedTokenObtainPairView, CustomizedTokenRefreshView

urlpatterns = [
    path('register/', views.registration_view),
    # path('login/', views.login_view),
    # jwt_token login and refresh
    path('login/', CustomizedTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', CustomizedTokenRefreshView.as_view(), name='token_refresh'),
    # #
    path('logout/', views.logout_view),
    path('reset_password/', views.reset_password_view)
]