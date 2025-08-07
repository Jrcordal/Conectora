from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django. contrib import messages
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required, user_passes_test
import pdfkit
from django.http import HttpResponse
from django.template import loader
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
import platform
import os
from django.urls import reverse_lazy
from .models import AuthorizedEmail
from django.utils import timezone
from django.contrib.auth.views import LoginView
from django.core.mail import send_mail
from django.conf import settings
from django.http import HttpResponseForbidden
from .forms import DeveloperProfileForm
from .models import DeveloperProfile
from .decorators import authorized_required
from .tasks import fill_developer_fields
@authorized_required
@login_required
def dashboard(request):
    return render(request, 'developers/dashboard.html')


@authorized_required
@login_required
def consent_form(request):
    try:
        profile = DeveloperProfile.objects.get(user=request.user)
        if profile.consent_promotional_use is not None:
            return redirect('developers:terms_and_conditions')
    except DeveloperProfile.DoesNotExist:
        profile = None

    if request.method == 'POST':
        consent_promo = 'consent_promotional_use' in request.POST

        DeveloperProfile.objects.update_or_create(
            user=request.user,
            defaults={
                'consent_promotional_use': consent_promo,
                'consent_given_at': timezone.now()
            }
        )

        return redirect('developers:profile_form')

    return render(request, 'developers/consent_form.html')


@authorized_required
@login_required
def privacy_settings(request):
    profile, created = DeveloperProfile.objects.get_or_create(user=request.user)

    if request.method == 'POST':
        consent_promo = 'consent_promotional_use' in request.POST
        profile.consent_promotional_use = consent_promo
        profile.consent_given_at = timezone.now()
        profile.save()
        messages.success(request, "Your privacy preferences have been updated.")
        return redirect('developers:profile_form')

    return render(request, 'developers/privacy_settings.html', {
        'profile': profile
    })

@authorized_required
@login_required
def terms_and_conditions(request):
    return render(request, 'developers/terms_and_conditions.html')


@authorized_required
@login_required
def profile_form(request):
    try:
        profile = DeveloperProfile.objects.get(user=request.user)
    except DeveloperProfile.DoesNotExist:
        return redirect('developers:consent_form')  # No hay perfil, no hay consentimiento

    if profile.consent_promotional_use is None:
        return redirect('developers:consent_form')  # Falta consentimiento explícito

    if request.method == 'POST':
        form = DeveloperProfileForm(request.POST, request.FILES, instance=profile)

        if form.is_valid():
            profile_instance = form.save(commit=False)

            # Actualizar CV si hay uno nuevo
            cv_file = request.FILES.get('cv_file')
            if cv_file:
                profile_instance.cv_file = cv_file
                profile_instance.cv_original_name = cv_file.name
                profile_instance.cv_size = cv_file.size
                profile_instance.cv_uploaded_at = timezone.now()
                fill_developer_fields.delay(profile_instance.id)
            elif not profile.cv_file:
                messages.error(request, 'You must upload your CV.')
                return render(request, 'developers/profile_form.html', {
                    'form': form,
                    'profile': profile,
                })

            profile_instance.save()

            messages.success(request, 'Your profile and CV have been updated correctly.')
            return redirect('developers:dashboard')

    else:
        form = DeveloperProfileForm(instance=profile)

    return render(request, 'developers/profile_form.html', {
        'form': form,
        'profile': profile,
    })

"""
@staff_member_required
def cv_pdf(request, id):
    user_profile = get_object_or_404(FreelancerProfile, pk=id) #get the user profile
    
    if not (request.user == user_profile.user or 
            request.user.is_staff):
        raise PermissionDenied

    # Detectar el sistema operativo y usar la ruta adecuada
    if platform.system() == 'Windows':
        wkhtmltopdf_path = r'C:/Program Files/wkhtmltopdf/bin/wkhtmltopdf.exe'
    else:
        # En Linux (Railway/Docker)
        wkhtmltopdf_path = '/usr/bin/wkhtmltopdf'
    
    config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)

    template = loader.get_template('freelancers/cv_clean.html') # get the template
    html = template.render({'user_profile': user_profile}) # render the template

    options = {
        'page-size': 'Letter',
        'encoding': "UTF-8",
    }
    pdf = pdfkit.from_string(html,False, options, configuration=config)
    response = HttpResponse(pdf, content_type='application/pdf')


    if user_profile.user.first_name and user_profile.user.last_name:
        name = f"{user_profile.user.first_name}_{user_profile.user.last_name}"
    elif user_profile.user.first_name:
        name = user_profile.user.first_name
    else:
        name = user_profile.user.username
    filename = f"CV_{name}.pdf"

    response['Content-Disposition'] = f'attachment; filename="{filename}"'
    return response




@login_required
def cv(request, id):
    try:
        # Convertir id a entero para evitar problemas de tipo
        user_id = int(id)
        # Obtener el perfil solicitado
        user = get_object_or_404(User, pk=user_id)
        try:
            profile = FreelancerProfile.objects.get(user_id=user_id)
            # Si es staff, puede ver cualquier perfil
            if request.user.is_staff:
                # admins can see any profile
                return render(request, 'freelancers/cv.html', {'user_profile':profile})
            # Si no es staff, solo puede ver su propio perfil
            elif request.user.id == user_id:
                return render(request, 'freelancers/cv.html', {'user_profile':profile})
            else:
                raise PermissionDenied("You don't have permission to see this CV")
            
        except FreelancerProfile.DoesNotExist: #if the profile does not exist
            if request.user.id == user_id: #if the user is the same as the one logged in
                messages.info(request, 'You have not created your profile yet')
                return redirect('freelancers:cv_form') #redirect to the form to create the profile
            elif request.user.is_staff:
                return render(request, 'freelancers/no_profile.html', {'user':profile, 'admin_view':True})
            else:
                raise PermissionDenied("You don't have permission to see this CV")

    except ValueError:
        raise Http404("Invalid profile ID")



@login_required
def redirect_to_cv(request):
    return redirect('freelancers:cv', id=request.user.id)

@login_required
def url_user_cv(request):
        user_cv_path = f"/freelancers/cv/{request.user.freelancerprofile.id}/"
        return render(request, "freelancers/cv.html", {"user_cv_path": user_cv_path})



@staff_member_required
def magic_link_manager(request):
    if request.method == 'POST':
        input_email = request.POST.get('email')

        if not input_email:
            messages.error(request, "Please enter a valid email.")
            return redirect('developers:magic_link_manager')

        # Crear token asociado al email
        magic_link = MagicToken.objects.create(user=input_email)

        # Enviar el email
        send_mail(
            'Magic Link',
            f'Send magic link to {input_email}: {magic_link.token}',
            'noreply@conectora.ai',
            [input_email],
            fail_silently=False,
        )

        return redirect('developers:magic_link_manager')

    # Mostrar todos los magic links
    magic_links = MagicToken.objects.all().order_by('-created_at')
    base_url = request.build_absolute_uri('/').rstrip('/')

    return render(request, 'developers/magic_link_manager.html', {
        'magic_links': magic_links,
        'base_url': base_url,
    })

"""
