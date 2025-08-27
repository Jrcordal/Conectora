from django.urls import path
from . import views as developer_views

app_name = 'developers'

urlpatterns = [    
    path('profile_form/',developer_views.profile_form, name='profile_form'),
    #path('cv/<int:id>',developer_views.cv, name = 'cv'),
    #path('redirect-to-cv/', developer_views.redirect_to_cv, name='redirect_to_cv'),
    path('consent/', developer_views.consent_form, name='consent_form'),
    path('terms-and-conditions/', developer_views.terms_and_conditions, name='terms_and_conditions'),
    path('dashboard/', developer_views.dashboard, name='dashboard'),
    path('settings/', developer_views.settings_view, name='settings_view'),
    path('admin_uploadcv/', developer_views.list_upload_cv, name='list')
    ]



