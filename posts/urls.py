from django.urls import path
from posts import views

urlpatterns = [
    path('all/', views.AllPostsView.as_view(), name='all posts'),
    path('id/<pk>/', views.EditPostView.as_view(), name='update post'),
    path('create/', views.CreatePostView.as_view(), name='create post'),
]