from django.urls import path
from account import views

urlpatterns = [
    path('register/', views.registration_view),
    path('login/', views.login_view),
    path('logout/', views.logout_view),
    path('reset_password/', views.reset_password_view)
]