from django.conf.urls import include, url
from django.urls import path, re_path
from django.contrib import admin
from django.views.generic import RedirectView
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.conf import settings
from rest_framework import routers
from server.views import account_views as a_views, game_views as g_views
from django.contrib.auth.views import LoginView
from server import urls as s_urls


urlpatterns = [
    path(r'', RedirectView.as_view(url='client/enter')),
    re_path(r'^accounts/login$', a_views.SignInView.as_view()),
    re_path(r'^accounts/sign_up$', a_views.SignUpView.as_view()),
    re_path(r'^accounts/enter$', a_views.EnterView.as_view()),
    re_path(r'^accounts/users/(?P<username>[\w\d_@\.\+\-]+)$', a_views.UserView.as_view()),
    re_path(r'^home$', g_views.GamesView.as_view()),
    re_path(r'^game/(?P<pk>\d+)$', g_views.GameView.as_view()),
    re_path(r'^new_game$', g_views.NewGameView.as_view()),
    re_path(r'^admin/', admin.site.urls),
    path('client/', include('client.urls')),
    path('server/', include(s_urls)),
    path('api-auth/', include('rest_framework.urls', namespace='rest_framework'))
]

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
