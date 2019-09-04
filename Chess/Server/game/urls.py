from django.urls import path
from . import views
from .views import GameViewSet
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'games', GameViewSet, basename='games')
urlpatterns = router.urls

# urlpatterns = [
#     path('games/', views.GameView.as_view(), name='games'),
#     path('games/<int:pk>', views.GameView.as_view(), name='games')
# ]
