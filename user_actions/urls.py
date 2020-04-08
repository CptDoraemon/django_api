from django.urls import path
from user_actions import views

urlpatterns = [
    path('like/', views.like_update_view, name='update like'),
    # path('save/', views.post_creation_view, name='update save'),
    path('all_liked/', views.all_liked_view, name='get all liked'),
    path('all_disliked/', views.all_disliked_view, name='get all disliked'),
    # path('all_saved/', views.post_creation_view, name='get all saved')
]