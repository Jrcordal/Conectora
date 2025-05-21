from django.urls import path
from . import views as user_views
from django.contrib.auth import views as authentication_views


urlpatterns = [    
    path('register/<uuid:token>/', user_views.register, name='register'),
    path('login/',authentication_views.LoginView.as_view(template_name ='users/login.html'), name='login'), #class based view (that is why .asview())
    path('logout/',user_views.logout_view, name='logout_view'),
    path('cv_form/',user_views.cv_form, name='cv_form'),
    path('<int:id>/pdf/',user_views.cv_pdf, name='cv_pdf'),
    path('list/',user_views.list, name='list'),
    path('<int:id>/cv/',user_views.cv, name = 'cv'),
    path('redirect-to-cv/', user_views.redirect_to_cv, name='redirect_to_cv'),
    path('mlmanager/', user_views.magic_link_manager, name='magic_link_manager'),
    path('consent/', user_views.consent_form, name='consent_form'),
    path('terms-and-conditions/', user_views.terms_and_conditions, name='terms_and_conditions'),
    ]