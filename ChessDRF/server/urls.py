from rest_framework import routers
from .views import drf_views
from django.conf.urls import include
from django.urls import path
import rest_registration.api.views as r_views

router = routers.DefaultRouter()
router.register(r'users', drf_views.UserViewSet)
router.register(r'figures', drf_views.FigureViewSet, basename='figures')
router.register(r'games', drf_views.GameViewSet, basename='games')

urlpatterns = [
    path('', include(router.urls)),
    path('accounts/login/', r_views.login),
    path('accounts/logout/', r_views.logout),
    path('accounts/profile/', r_views.profile),
    path('accounts/register/', drf_views.register),
    # path('accounts/', include('rest_registration.api.urls')),
    # path('login', drf_views.login),
]
