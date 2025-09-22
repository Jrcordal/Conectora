from django.shortcuts import render, redirect
from .models import ClientProfile
from .forms import ClientProfileForm
from apps.clients.decorators import authorized_required
from django.utils import timezone
from django.contrib.auth.decorators import login_required

# Create your views here.




@authorized_required
def dashboard(request):
 
    return render(request, 'clients/dashboard.html')




@login_required
@authorized_required
def profile_form(request):
    profile, created = ClientProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        form = ClientProfileForm(request.POST, request.FILES, instance=profile)

        if form.is_valid():
            profile = form.save()  # guarda directamente en la DB

            return redirect('clients:dashboard')

    else:
        form = ClientProfileForm(instance=profile)

    return render(request, 'clients/profile_form.html', {
        'form': form,
        'profile': profile,
    })