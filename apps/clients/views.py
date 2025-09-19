from django.shortcuts import render

from apps.clients.decorators import authorized_required

# Create your views here.




@authorized_required
def dashboard(request):
 
    return render(request, 'clients/dashboard.html')