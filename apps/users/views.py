from django.shortcuts import render, redirect
from django. contrib import messages
from .forms import CustomUserCreationForm, CustomAuthenticationForm
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required

import io
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from bs4 import BeautifulSoup
from django.core.exceptions import ValidationError
from django.http import Http404
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from django.contrib.admin.views.decorators import staff_member_required
from django.contrib.auth.forms import PasswordResetForm
from apps.users.models import CustomUser
from django.core.mail import EmailMultiAlternatives
from django.template import loader



from django.urls import reverse_lazy

from django.utils import timezone
from django.contrib.auth.views import LoginView, PasswordResetView
import logging


logger = logging.getLogger(__name__)

class CustomLoginView(LoginView):
    template_name = "registration/login.html"
    authentication_form = CustomAuthenticationForm
    redirect_authenticated_user = True  # Si ya está logueado, redirige automáticamente
    success_url = reverse_lazy("users:dashboard")  # Dónde enviar tras login




class CustomPasswordReset(PasswordResetForm):
    def clean_email(self):
        data = self.cleaned_data['email']
        if not CustomUser.objects.filter(email=data).exists():
            raise ValidationError("Email does not exist")
        return data

    def send_mail(self, subject_template_name, email_template_name, context,
                  from_email, to_email, html_email_template_name=None):
        # Renderiza asunto y cuerpo
        subject = loader.render_to_string(subject_template_name, context)
        subject = "".join(subject.splitlines())
        body = loader.render_to_string(email_template_name, context)

        email_message = EmailMultiAlternatives(subject, body, from_email, [to_email])
        if html_email_template_name is not None:
            html_email = loader.render_to_string(html_email_template_name, context)
            email_message.attach_alternative(html_email, "text/html")

        # Enviar el email (si falla, lanza error en desarrollo)
        email_message.send(fail_silently=False)

class CustomPasswordResetView(PasswordResetView):
    """Vista personalizada para password reset que captura errores de envío"""
    template_name = 'registration/password_reset_form.html'
    email_template_name = 'registration/password_reset_email.html'
    subject_template_name = 'registration/password_reset_subject.txt'
    success_url = reverse_lazy('users:password_reset_done')
    
    def form_valid(self, form):
        """Override para capturar errores de envío de correo"""
        try:
            # Llamar al método original pero capturando errores
            response = super().form_valid(form)
            return response
            
        except Exception as e:
            # Mostrar el error al usuario en lugar de fallar silenciosamente
            messages.error(
                self.request, 
                f"Error al enviar el correo de restablecimiento: {str(e)}"
            )
            return self.form_invalid(form)

# Create your views here.
def register(request):
    if request.method == 'POST':
        form = CustomUserCreationForm(request.POST)
        if form.is_valid():
            with transaction.atomic(): # type: ignore
                user_saved = form.save()

            username = form.cleaned_data.get('username')
            messages.success(request, f'Welcome {username}, your account is created!')

            # Autenticar y hacer login automático
            user = authenticate(
                username=form.cleaned_data.get('username'),
                password=form.cleaned_data.get('password1')
            )
            if user is not None:
                login(request, user)
                return redirect('users:dashboard')  # Cambia esto a tu vista destino

        # Mostrar errores del formulario
        elif form.errors:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.warning(request, f'Error in {field}: {error}')
    else:
        form = CustomUserCreationForm()
    
    return render(request, 'registration/register.html', {'form': form})

@login_required
def logout_view(request):
    if request.method == "POST":  # Ensure that it only occurs with POST
        logout(request)
        return redirect('users:login')  # Redirects after logout
    return render(request, 'registration/logout.html')  # if GET, shows the form

@login_required
def dashboard(request):
    return render(request, 'users/dashboard.html')

