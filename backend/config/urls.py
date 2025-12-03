from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from drf_spectacular.views import SpectacularAPIView, SpectacularSwaggerView

from users.views import RegisterView

urlpatterns = [
    path('admin/', admin.site.urls),

    path('api/auth/register/', RegisterView.as_view(), name='custom_register'),
    path('api/auth/', include('dj_rest_auth.urls')),

    path('api/', include('transactions.urls')),
    path('api/splitting/', include('splitting.urls')),
    path('api/social/', include('social.urls')),
    path('api/integrations/', include('integrations.urls')),
    path('api/reports/', include('reports.urls')),
    path('api/schema/', SpectacularAPIView.as_view(), name='schema'),
    path('api/docs/', SpectacularSwaggerView.as_view(url_name='schema'), name='swagger-ui'),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
