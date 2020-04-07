from django.urls import path
from comments import views

urlpatterns = [
    path('create/', views.comment_creation_view, name='create comment'),
    # path('get/<int:comment_id>/', views.AllPostsView.as_view(), name='get one comment'),
    path('edit/<int:comment_id>/', views.comment_edit_view, name='edit comment'),
    path('delete/<int:comment_id>/', views.comment_deletion_view, name='delete comment'),
    path('all/', views.AllCommentsView.as_view(), name='all comments'),
]