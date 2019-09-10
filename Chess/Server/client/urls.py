from django.urls import path
from . import views
from django.contrib.auth.views import LoginView


urlpatterns = [
    path('enter', LoginView.as_view(template_name='client/login.html')),
    path('games/', views.GameListView.as_view()),
    path('games/<int:pk>', views.GameView.as_view())
]
