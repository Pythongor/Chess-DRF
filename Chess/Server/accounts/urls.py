from django.urls import path
from . import views


urlpatterns = [
    path('get_token', views.login),
    path('users', views.UserView.as_view()),
    path('users/<pk>', views.UserView.as_view()),
]
