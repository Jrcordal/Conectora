from .models import AuthorizedClientEmail
from django.shortcuts import render
from apps.developers.decorators import email_authorized as developer_email_authorized
from django.conf import settings
from functools import wraps

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


def prompt_limit_reached_required(view_func):
    @wraps(view_func)
    def _wrapped_view(request, *args, **kwargs):
        profile = getattr(request.user, "clientprofile", None)

        if not profile:
            return render(request, 'clients/prompt_limit_reached.html', status=403)

        if profile.search_limit <= 0:
            return render(request, 'clients/prompt_limit_reached.html', status=403)

        return view_func(request, *args, **kwargs)

    return _wrapped_view