from django.urls import path
from . import views

app_name = 'companies'

urlpatterns = [
    path('setup/', views.company_setup_view, name='company_setup'),
    path('settings/', views.company_settings_view, name='company_settings'),
]