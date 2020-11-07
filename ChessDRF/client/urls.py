from rest_framework import routers
from django.conf.urls import include
from django.urls import path
from .views import account_views, game_views

urlpatterns = [
    path('home', game_views.GamesView.as_view(), name='home'),
    path('game/<id>', game_views.GameView.as_view(), name='game'),
    path('new_game', game_views.NewGameView.as_view(), name='new_game'),
    path('enter', account_views.EnterView.as_view(), name='enter'),
    path('login', account_views.LoginView.as_view(), name='login'),
    path('signup', account_views.SignUpView.as_view(), name='signup'),
    path('users/<username>', account_views.ProfileView.as_view(), name='profile'),
]
