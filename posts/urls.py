from django.urls import path
from posts import views

urlpatterns = [
    path('<slug>/', views.detail_post_view, name='post detail'),
    path('update/<slug>/', views.update_post_view, name='update post'),
    path('delete/<slug>/', views.delete_post_view, name='delete post'),
    path('create/', views.create_post_view, name='create post')
]