from django.urls import path, reverse_lazy
from . import views as users_views
from django.contrib.auth import views as auth_views
from django.contrib.auth.decorators import login_required

from django.conf import settings
app_name = 'users' # adds this to the namespace

urlpatterns = [    
    path('register/', users_views.register, name='register'),
    path('login/', users_views.CustomLoginView.as_view(), name='login'),
    path('logout/',users_views.logout_view, name='logout_view'),
    path('dashboard/',users_views.dashboard, name='dashboard'),
    path('password_change/',login_required(auth_views.PasswordChangeView.as_view(success_url=reverse_lazy('users:password_change_done'),template_name='registration/password_change_form.html')), name='password_change'),
    path('password_change/done/',login_required(auth_views.PasswordChangeDoneView.as_view(template_name='registration/password_change_done.html')), name='password_change_done'),
    path('password_reset/',auth_views.PasswordResetView.as_view(
        template_name='registration/password_reset_form.html',
        email_template_name='registration/password_reset_email.html',
        subject_template_name='registration/password_reset_subject.txt', 
        success_url=reverse_lazy('users:password_reset_done')
    ), name='password_reset'),
    path('password_reset/done/',auth_views.PasswordResetDoneView.as_view(template_name='registration/password_reset_done.html'), name='password_reset_done'),
    path('password_reset/confirm/<uidb64>/<token>/',auth_views.PasswordResetConfirmView.as_view(success_url=reverse_lazy('users:password_reset_complete'),template_name='registration/password_reset_confirm.html'), name='password_reset_confirm'),
    path('password_reset/complete/',auth_views.PasswordResetCompleteView.as_view(template_name='registration/password_reset_complete.html'), name='password_reset_complete'),
    ]
