from django.urls import path
from . import views


app_name = 'cloud_provider'

urlpatterns = [
    path('', views.dashboard, name='dashboard'),
    path('connect/', views.connect_provider, name='connect_provider'),
    path('connect/google-drive/', views.connect_google_drive, name='connect_google_drive'),
    path('connect/onedrive/', views.connect_onedrive, name='connect_onedrive'),
    path('callback/google-drive/', views.google_drive_callback, name='google_drive_callback'),
    path('callback/onedrive/', views.onedrive_callback, name='onedrive_callback'),
    path('disconnect/<int:provider_id>/', views.disconnect_provider, name='disconnect_provider'),
]