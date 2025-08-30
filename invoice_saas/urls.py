"""
URL configuration for invoice_saas project.
"""
from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static
from django.contrib.auth import views as auth_views
from invoice_management.views import dashboard_view

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', dashboard_view, name='dashboard'),
    path('auth/', include('authentication.urls')),
    path('company/', include('companies.urls')),
    path('invoices/', include('invoice_management.urls')),
    path('logout/', auth_views.LogoutView.as_view(), name='logout'),
]

# Serve media files in development
if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
    urlpatterns += static(settings.STATIC_URL, document_root=settings.STATIC_ROOT)
