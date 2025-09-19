from django.urls import path
from . import views as client_views

app_name = 'clients'

urlpatterns = [    
    path('dashboard/', client_views.dashboard, name='dashboard'),
    
    ]