from django.shortcuts import render, redirect
from django.contrib.auth.forms import UserCreationForm
from django. contrib import messages
from .forms import RegisterForm
from django.contrib.auth import logout
from django.contrib.auth.decorators import login_required, user_passes_test
from .models import Profile
import pdfkit
from django.http import HttpResponse
from django.template import loader
import io
from django.db import transaction
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from bs4 import BeautifulSoup
from django.core.exceptions import ValidationError
from .forms import ProfileForm
from django.http import Http404
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
from .models import MagicLink
from django.contrib.admin.views.decorators import staff_member_required
import platform
import os
from django.urls import reverse
#def staff_required(user):
#    return user.is_staff
#@user_passes_test(staff_required)
from django.utils import timezone

def register(request, token):
    magic_link = get_object_or_404(MagicLink, token=token)

    if not magic_link.is_valid():
        raise Http404("Invalid or expired link.")

    if request.method == 'POST':
        form = RegisterForm(request.POST)
        if form.is_valid():
            with transaction.atomic():
                user_saved = form.save()
                Profile.objects.get_or_create(user=user_saved)
                magic_link.used = True
                magic_link.save()
            username = form.cleaned_data.get('username')
            messages.success(request, f'Welcome {username}, your account is created')
            return redirect('login')
        elif form.errors: #check for errors in the form 
            for field, errors in form.errors.items():
                for error in errors:
                    messages.warning(request, f'Error in {field}: {error}')
    else: #if request method is not POST but GET. 1st time the page is loaded
        form = RegisterForm() #create a new form
    return render(request, 'users/register.html', {'form': form})





@login_required
def logout_view(request):
    if request.method == "POST":  # Ensure that it only occurs with POST
        logout(request)
        return redirect('login')  # Redirects after logout
    return render(request, 'users/logout.html')  # if GET, shows the form




@login_required
def consent_form(request):
    # Si el perfil ya existe, redirige directamente a 'cv_form'
    if Profile.objects.filter(user=request.user).exists():
        return redirect('terms_and_conditions')

    # Si no existe, permite mostrar el formulario y guardar datos
    if request.method == 'POST':
        consent_promo = bool(request.POST.get('consent_promotional_use'))

        profile = Profile.objects.create(
            user=request.user,
            consent_promotional_use=consent_promo,
            consent_given_at=timezone.now()
        )

        return redirect('cv_form')

    return render(request, 'users/consent_form.html')

@login_required
def terms_and_conditions(request):
    return render(request, 'users/terms_and_conditions.html')


@login_required
def cv_form(request):

    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        return redirect('consent_form')  # No hay perfil, no hay consentimiento

    if profile.consent_promotional_use is None:
        return redirect('consent_form')  # Falta consentimiento explícito
    # Fields that should be converted from lists to newline-separated text for the form
    list_fields = ['university_education', 'education_certificates', 'experience', 'skills', 'projects', 'interests', 'volunteering', 'languages']
    non_list_fields = ['hourly_rate']

    if request.method == 'POST':
        # Mantener la estructura condicional para determinar si estamos creando o actualizando
        if profile:
            form = ProfileForm(request.POST, instance=profile)
        else:
            form = ProfileForm(request.POST)
        
        if form.is_valid(): #check if the form is valid
            # Don't save yet - we need to process the list fields
            profile_instance = form.save(commit=False)
            
            # Convert newline-separated text to lists for JSON fields
            for field in list_fields:
                text_value = form.cleaned_data[field]
                if text_value:
                    # Split by newlines and remove empty lines
                    list_value = [line.strip() for line in text_value.split('\n') if line.strip()]
                    setattr(profile_instance, field, list_value)
                else:
                    setattr(profile_instance, field, None)
            for field in non_list_fields:
                text_value = form.cleaned_data[field]
                if text_value:
                    setattr(profile_instance, field, text_value)
                else:
                    setattr(profile_instance, field, None)
            
            # Set user if this is a new profile
            if not profile:
                profile_instance.user = request.user
            
            profile_instance.save()
            messages.success(request, 'Your CV has been updated correctly.')
            return redirect('cv', id=request.user.id)
            
    else:
        # For GET requests, create a form with the current data
        if profile:
            # Convert lists to newline-separated text for display in the form
            initial_data = {}
            for field in list_fields:
                field_value = getattr(profile, field, None)
                if field_value and len(field_value) > 0:
                    initial_data[field] = '\n'.join(field_value)
                else:
                    initial_data[field] = ''
            
            form = ProfileForm(instance=profile, initial=initial_data)
        else:
            form = ProfileForm()
    
    return render(request, 'users/cv_generator.html', {
        'form': form,
        'profile': profile,
        'is_new_profile': profile is None
    })
   

@staff_member_required
def cv_pdf(request, id):
    user_profile = get_object_or_404(Profile, pk=id) #get the user profile
    
    if not (request.user == user_profile.user or 
            request.user.is_staff):
        raise PermissionDenied

    # Detectar el sistema operativo y usar la ruta adecuada
    if platform.system() == 'Windows':
        wkhtmltopdf_path = r'C:\Program Files\wkhtmltopdf\bin\wkhtmltopdf.exe'
    else:
        # En Linux (Railway/Docker)
        wkhtmltopdf_path = '/usr/bin/wkhtmltopdf'
    
    config = pdfkit.configuration(wkhtmltopdf=wkhtmltopdf_path)

    template = loader.get_template('users/cv_clean.html') # get the template
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
            profile = Profile.objects.get(user_id=user_id)
            # Si es staff, puede ver cualquier perfil
            if request.user.is_staff:
                # admins can see any profile
                return render(request, 'users/cv.html', {'user_profile':profile})
            # Si no es staff, solo puede ver su propio perfil
            elif request.user.id == user_id:
                return render(request, 'users/cv.html', {'user_profile':profile})
            else:
                raise PermissionDenied("You don't have permission to see this CV")
            
        except Profile.DoesNotExist: #if the profile does not exist
            if request.user.id == user_id: #if the user is the same as the one logged in
                messages.info(request, 'You have not created your profile yet')
                return redirect('cv_form') #redirect to the form to create the profile
            elif request.user.is_staff:
                return render(request, 'users/no_profile.html', {'user':profile, 'admin_view':True})
            else:
                raise PermissionDenied("You don't have permission to see this CV")

    except ValueError:
        raise Http404("Invalid profile ID")

@login_required
def list(request):
    if not (request.user.is_staff):
        raise PermissionDenied
        #return redirect('cv', id=request.user.pk)
    profiles = Profile.objects.all()
    return render(request,'users/list.html',{'profiles':profiles})

@login_required
def redirect_to_cv(request):
    return redirect('cv', id=request.user.id)

@login_required
def url_user_cv(request):
        user_cv_path = f"/cv/{request.user.profile.id}/"
        return render(request, "users/cv.html", {"user_cv_path": user_cv_path})







@staff_member_required
def magic_link_manager(request):
    if request.method == 'POST':
        magic_link = MagicLink.objects.create()
        return redirect('magic_link_manager')

    magic_links = MagicLink.objects.all().order_by('-created_at')
    base_url = request.build_absolute_uri('/').rstrip('/')

    return render(request, 'users/magic_link_manager.html', {
        'magic_links': magic_links,
        'base_url': base_url,
    })

