from django.urls import path
from . import views as freelancer_views

app_name = 'freelancers'

urlpatterns = [    
    path('register/<uuid:token>/', freelancer_views.register, name='register'),
    path('login/', freelancer_views.FreelancerLoginView.as_view(template_name='freelancers/login.html'), name='freelancer_login'),
    path('logout/',freelancer_views.logout_view, name='logout_view'),
    path('cv_form/',freelancer_views.cv_form, name='cv_form'),
    path('pdf/<int:id>',freelancer_views.cv_pdf, name='cv_pdf'),
    path('list/',freelancer_views.list, name='list'),
    path('cv/<int:id>',freelancer_views.cv, name = 'cv'),
    path('redirect-to-cv/', freelancer_views.redirect_to_cv, name='redirect_to_cv'),
    path('mlmanager/', freelancer_views.magic_link_manager, name='magic_link_manager'),
    path('consent/', freelancer_views.consent_form, name='consent_form'),
    path('terms-and-conditions/', freelancer_views.terms_and_conditions, name='terms_and_conditions'),
    ]