from django.urls import path
from posts import views

urlpatterns = [
    path('all/', views.AllPostsView.as_view(), name='all posts'),
    path('create/', views.post_creation_view, name='create post'),
    path('edit/<int:post_id>/', views.post_edit_view, name='update post'),
    path('delete/<int:post_id>/', views.post_deletion_view, name='delete post'),
]