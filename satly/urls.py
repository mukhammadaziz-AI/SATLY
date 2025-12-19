from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from app.custom_admin import satly_admin_site

urlpatterns = [
    path('django-admin/', satly_admin_site.urls),
    path('accounts/', include('allauth.urls')),
    path('', include('app.urls')),
]

handler404 = 'app.views.error_404'
handler500 = 'app.views.error_500'

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
else:
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATICFILES_DIRS[0])
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)