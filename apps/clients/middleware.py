from django.urls import resolve
from .models import ClientProfile

class EnsureClientProfileMiddleware:
    CLIENT_NAMESPACE = "clients"

    def __init__(self, get_response):
        self.get_response = get_response

    def __call__(self, request):
        user = getattr(request, "user", None)
        if user and user.is_authenticated:
            try:
                match = resolve(request.path_info) # path info gives you the url without clients/
                if match.namespace == self.CLIENT_NAMESPACE: # namespace is 'clients'
                    ClientProfile.objects.get_or_create(user=user)
            except Exception:
                pass
        return self.get_response(request)
