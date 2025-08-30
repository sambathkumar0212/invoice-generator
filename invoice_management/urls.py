from django.urls import path
from . import views

app_name = 'invoice_management'

urlpatterns = [
    path('', views.invoice_list_view, name='invoice_list'),
    path('create/', views.invoice_create_view, name='invoice_create'),
    path('<int:pk>/', views.invoice_detail_view, name='invoice_detail'),
    path('<int:pk>/edit/', views.invoice_edit_view, name='invoice_edit'),
    path('<int:pk>/pdf/', views.invoice_pdf_view, name='invoice_pdf'),
    path('<int:pk>/status/', views.invoice_status_update, name='invoice_status_update'),
    path('clients/', views.client_list_view, name='client_list'),
    path('clients/create/', views.client_create_view, name='client_create'),
]