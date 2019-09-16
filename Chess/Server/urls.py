from django.urls import path
from . import views
from .views import GameViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'games', GameViewSet, basename='games')

urlpatterns = [path('get_token', views.login), path('users', views.UserView.as_view()),
               path('users/<pk>', views.UserView.as_view()), *router.urls]

# urlpatterns = [
#     path('games/', views.GameView.as_view(), name='games'),
#     path('games/<int:pk>', views.GameView.as_view(), name='games')
# ]
