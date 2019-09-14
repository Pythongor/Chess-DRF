from django.urls import path
from . import views
from django.contrib.auth.views import LoginView


urlpatterns = [
    path('enter', LoginView.as_view(template_name='client/login.html')),
    path('games/', views.GameListView.as_view()),
    path('games/<int:pk>', views.GameView.as_view()),
    path('games/new_game/<username>', views.invite, name='new game'),
    path('games/invite/<int:pk>', views.InvitedGame.as_view, name='invited'),
    path('games/delete/<int:pk>', views.delete, name='delete'),
    path('games/accept_invite/<int:pk>', views.accept_invite, name='accept'),
]
