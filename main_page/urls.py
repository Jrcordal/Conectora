
from django.contrib import admin
from django.urls import include, path
from . import views as main_views


urlpatterns = [
    path('', main_views.main, name='main'),
    path('admin/', admin.site.urls),
    path('users/', include('apps.users.urls')),
    path('developers/', include('apps.developers.urls', namespace='developers')),

    ]





from django.conf import settings
from django.conf.urls.static import static
# Solo en desarrollo: sirve archivos MEDIA desde MEDIA_ROOT
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)