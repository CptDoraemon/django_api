"""django_api URL Configuration

The `urlpatterns` list routes URLs to views. For more information please see:
    https://docs.djangoproject.com/en/3.0/topics/http/urls/
Examples:
Function views
    1. Add an import:  from my_app import views
    2. Add a URL to urlpatterns:  path('', views.home, name='home')
Class-based views
    1. Add an import:  from other_app.views import Home
    2. Add a URL to urlpatterns:  path('', Home.as_view(), name='home')
Including another URLconf
    1. Import the include() function: from django.urls import include, path
    2. Add a URL to urlpatterns:  path('blog/', include('blog.urls'))
"""
from django.contrib import admin
from django.urls import include, path
from jwt_token.views import CustomizedTokenObtainPairView, CustomizedTokenRefreshView


urlpatterns = [
    path('admin/', admin.site.urls),
    # jwt_token login and refresh
    path('api/token/', CustomizedTokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('api/refresh/', CustomizedTokenRefreshView.as_view(), name='token_refresh'),
    # #
    path('api/discussion_board/post/', include('posts.urls')),
    path('api/discussion_board/account/', include('account.urls')),
    path('api/discussion_board/comment/', include('comments.urls')),
    path('api/discussion_board/user_actions/', include('user_actions.urls')),
]
