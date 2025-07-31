from django.http import HttpResponseForbidden
from django.contrib.auth.decorators import user_passes_test
from .models import AuthorizedEmail
from django.shortcuts import render


def email_authorized(user):
    return AuthorizedEmail.objects.filter(email=user.email, active=True).exists()

def authorized_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        # Verificar si el usuario está autorizado
        if not email_authorized(request.user):
            return render(request, 'developers/unauthorized.html', status=403)
        return view_func(request, *args, **kwargs)
    return _wrapped_view