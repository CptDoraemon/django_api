from django.urls import path
from posts import views

urlpatterns = [
    path('all/', views.all_posts_view, name='all posts'),
    path('<int:pk>/', views.post_detail_view, name='post detail'),
    path('create/', views.post_creation_view, name='create post'),
    path('edit/<int:post_id>/', views.post_edit_view, name='update post'),
    path('delete/<int:post_id>/', views.post_deletion_view, name='delete post'),
    path('tag-list/', views.post_tag_list_view, name='post tag list'),
    path('pin/', views.pin_post_view, name='pin post'),
    path('pinned-posts/', views.pinned_posts_view, name='all pinned posts'),
]