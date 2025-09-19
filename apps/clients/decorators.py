from .models import AuthorizedClientEmail
from django.shortcuts import render
from apps.developers.decorators import email_authorized as developer_email_authorized
from django.conf import settings

def email_authorized(user):
    return AuthorizedClientEmail.objects.filter(email=user.email, active=True).exists()

def authorized_required(view_func):
    def _wrapped_view(request, *args, **kwargs):
        # Si la autorización está desactivada en settings → permitir todo
        if not getattr(settings, "AUTHORIZE_CLIENTS_BY_LIST", False):
            return view_func(request, *args, **kwargs)

        # Si está activada → chequear client o developer autorizado
        if not (email_authorized(request.user) or developer_email_authorized(request.user)):
            return render(request, 'clients/unauthorized.html', status=403)

        return view_func(request, *args, **kwargs)
    return _wrapped_view