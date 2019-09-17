from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.staticfiles.urls import staticfiles_urlpatterns
from django.views.generic import RedirectView

urlpatterns = [
    path('', RedirectView.as_view(url='client/register')),
    # path('admin/', admin.site.urls),
    path('server/', include('server.urls')),
    path('client/', include('client.urls')),
]

urlpatterns += staticfiles_urlpatterns()
urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)