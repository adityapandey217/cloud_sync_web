from django.urls import path
from . import views
from django.urls import include

urlpatterns = [
    path('accounts/', include('allauth.urls')),
]