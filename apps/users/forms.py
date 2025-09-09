from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
import phonenumbers
from django.core.exceptions import ValidationError
from django.contrib.auth.forms import AdminUserCreationForm, UserChangeForm
from .models import CustomUser, TIMEZONE_CHOICES, ROLE_CHOICES
import logging
from django.contrib.auth import authenticate
from django.forms.widgets import ClearableFileInput

class CustomUserAdminCreationForm(AdminUserCreationForm):

    class Meta:
        model = CustomUser
        fields = ("username", "email", "first_name", "last_name", "timezone", "role")

class CustomUserAdminChangeForm(UserChangeForm):

    class Meta:
        model = CustomUser
        fields = ("username", "email", "first_name", "last_name", "timezone", "role")



class CustomUserCreationForm(UserCreationForm):
    email = forms.EmailField() # email field is required by default so no need to specify it in clean method
    timezone = forms.ChoiceField(
        choices=[('', 'Select your timezone')] + TIMEZONE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    role = forms.ChoiceField(
        choices=[('', 'Select your role')] + ROLE_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )
    #phone = forms.CharField(max_length=15)
    class Meta(UserCreationForm.Meta): # Meta class holds information about CustomUserCreationForm class
        model = CustomUser
        fields = ("username", "password1", "password2", "first_name", "last_name", "email", "timezone", "role")
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if CustomUser.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already in use.")
        return email
    

    def clean(self):
        cleaned_data = super().clean() # super() is used to call the parent class (UserCreationForm) and clean() is used to validate the form
        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')
        timezone = cleaned_data.get('timezone')
        role = cleaned_data.get('role')
        
        if not first_name:
            raise forms.ValidationError('First name is mandatory')
        if not last_name:
            raise forms.ValidationError('Last name is mandatory')
        if not timezone:
            raise forms.ValidationError('Timezone is mandatory')
        if not role:
            raise forms.ValidationError('At least one role is mandatory')
                    
        return cleaned_data
    
    #def clean_phone(self):
    #    return validate_phone(self.cleaned_data.get('phone'))



class CustomAuthenticationForm(AuthenticationForm):
    # Usamos 'username' porque Django lo espera, pero lo mostramos como Email
    username = forms.EmailField(
        label="Email",
        widget=forms.EmailInput(attrs={'autofocus': True})
    )

    def clean(self):
        email = self.cleaned_data.get('username')  # sigue llamándose 'username'
        password = self.cleaned_data.get('password')

        if email and password:
            self.user_cache = authenticate(self.request, username=email, password=password)

            if self.user_cache is None:
                raise forms.ValidationError("Email o contraseña incorrectos.")

        return self.cleaned_data
    


class MultipleFileInput(forms.ClearableFileInput):
    # Habilita múltiples ficheros
    allow_multiple_selected = True

class MultipleCvsUploadForm(forms.Form):
    files = forms.FileField(
        label="CV files",
        widget=MultipleFileInput(attrs={"accept": ".pdf,.docx"}),
        required=True,
        help_text="Puedes seleccionar varios .pdf o .docx."
    )