from django.urls import path
from tutorial_snippets import views
from rest_framework.urlpatterns import format_suffix_patterns
from django.conf.urls import include

urlpatterns = format_suffix_patterns([
    path('', views.api_root),
    path('tutorial_snippets/',
         views.SnippetList.as_view(),
         name='snippet-list'),
    path('tutorial_snippets/<int:pk>/',
         views.SnippetDetail.as_view(),
         name='snippet-detail'),
    path('tutorial_snippets/<int:pk>/highlight/',
         views.SnippetHighlight.as_view(),
         name='snippet-highlight'),
    path('users/',
         views.UserList.as_view(),
         name='user-list'),
    path('users/<int:pk>/',
         views.UserDetail.as_view(),
         name='user-detail')
])

urlpatterns += [
    path('api-auth/', include('rest_framework.urls')),
]
