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
from django.shortcuts import get_object_or_404
from django.core.exceptions import PermissionDenied
from bs4 import BeautifulSoup
from django.core.exceptions import ValidationError
from .forms import ProfileForm
from django.http import Http404
from django.contrib.auth import authenticate, login
from django.contrib.auth.models import User
#def staff_required(user):
#    return user.is_staff
#@user_passes_test(staff_required)



#Insert magic link here for unique access to users
def register(request): 
    if request.method == 'POST': # Check if request method is POST
        form = RegisterForm(request.POST)
        if form.is_valid(): #check for duplicates
            form.save() # save user. commit=False means that the user is not saved yet
            Profile.objects.create(user=form.instance)
            username= form.cleaned_data.get('username') # extract user name from form
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
def cv_form(request):
    # Intenta obtener el perfil o None si no existe
    try:
        profile = Profile.objects.get(user=request.user)
    except Profile.DoesNotExist:
        profile = None


    
    if request.method == 'POST':
        if profile:
            form = ProfileForm(request.POST, request.FILES, instance=profile)
        else:
            form = ProfileForm(request.POST, request.FILES)
            
        if form.is_valid():
            if not profile:
                profile = form.save(commit=False) # save the form but don't commit to the database yet because we need to set the user field
                profile.user = request.user # set the user field to the current user
                profile.save() # then it is possible tosave the profile to the database
            else:
                form.save()
                
            messages.success(request, 'Your CV has been updated correctly.')
            return redirect('cv', id=request.user.id)
        elif form.errors:
            for field, errors in form.errors.items():
                for error in errors:
                    messages.warning(request, f'Error in {field}: {error}')
    else:
        if profile:
            form = ProfileForm(instance=profile)
        else:
            form = ProfileForm()
    
    return render(request, 'users/cv_generator.html', {
        'form': form,
        'profile': profile,
        'is_new_profile': profile is None
    })
   

@login_required
def cv_pdf(request, id):
    user_profile = get_object_or_404(Profile, pk=id) #get the user profile
    
    if not (request.user == user_profile.user or 
            request.user.is_staff):
        raise PermissionDenied



    template = loader.get_template('users/cv_clean.html') # get the template
    html = template.render({'user_profile': user_profile}) # render the template

    options = {
        'page-size': 'Letter',
        'encoding': "UTF-8",
    }
    config = pdfkit.configuration(wkhtmltopdf = r'C:\wkhtmltox\bin\wkhtmltopdf.exe')
    pdf = pdfkit.from_string(html,False, options, configuration=config)
    response = HttpResponse(pdf, content_type='application/pdf')
    response['Content-Disposition'] = 'attachment'
    filename = "cv.pdf"
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
                return render(request, 'users/cv.hmtl', {'user_profile':user})
            # Si no es staff, solo puede ver su propio perfil
            elif request.user.id == user_id:
                return render(request, 'users/cv.html', {'user_profile':user})
            else:
                raise PermissionDenied("You don't have permission to see this CV")
            
        except Profile.DoesNotExist:
            if request.user.id == user_id:
                messages.info(request, 'You have not created your profile yet')
                return redirect('cv_form')
            elif request.user.is_staff:
                return render(request, 'users/no_profile.html', {'user':user, 'admin_view':True})
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




