"""
URL configuration for smartkeja project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    # Django auth (login/logout/password reset)
    path('accounts/', include('django.contrib.auth.urls')),
    # Main app - include at root for backward compatibility
    path('', include('properties.urls')),
    # Also include under properties/ prefix (both work)
    path('properties/', include('properties.urls')),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)

