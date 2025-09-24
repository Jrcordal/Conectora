from django.urls import path
from . import views as client_views

app_name = 'clients'

urlpatterns = [    
    path('dashboard/', client_views.dashboard, name='dashboard'),
    path('profile_form/',client_views.profile_form, name='profile_form'),
    path('intake/',client_views.intake, name='intake')
    ]