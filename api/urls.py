from django.urls import path
from . import views

urlpatterns = [
    path('register', views.register, name='register'),
    path('auth/register', views.register, name='auth_register'),
    path('login/', views.login_view, name='login'),
    path('auth/login/', views.login_view, name='auth_login'),
    path('users/', views.search_users, name='search_users'),
    path('conversations/', views.conversations_view, name='conversations'),
    path('conversation/<int:id>/messages/', views.conversation_messages_view, name='conversation_messages'),
    path('messages/', views.send_message_view, name='send_message'),
    path('games', views.games_view, name='games'),
]
