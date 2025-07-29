from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
import phonenumbers
from django.core.exceptions import ValidationError
from .models import DeveloperProfile
from django_countries.fields import CountryField


#def validate_phone(value):
#    try:
#        phone_number = phonenumbers.parse(str(value))
#    except phonenumbers.phonenumberutil.NumberParseException:
#        raise ValidationError("Invalid phone number format. Please include country code (e.g. +31)")
#    if not phonenumbers.is_valid_number(phone_number):
#        raise ValidationError("This is not a valid phone number")
#    return phonenumbers.format_number(phone_number, phonenumbers.PhoneNumberFormat.E164)
   


            
class DeveloperProfileForm(forms.ModelForm):
   
    cv_file = forms.FileField(
        required=True,
        widget=forms.FileInput(attrs={
            'class': 'form-control',
            'accept': '.pdf,.doc,.docx,.txt'
        })
    )

    country_living_in = CountryField(blank_label="(Select country)").formfield()
    nationality = CountryField(blank_label="(Select country)").formfield()
 

   
    
    linkedin = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            'placeholder': 'E.g.: https://linkedin.com/in/yourprofile',
            'class': 'form-control'
        })
    )
    
    github = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            'placeholder': 'E.g.: https://github.com/yourusername',
            'class': 'form-control'
        })
    )
    
    personal_website = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            'placeholder': 'E.g.: https://yourpersonalwebsite.com',
            'class': 'form-control'
        })
    )
    
    hourly_rate = forms.DecimalField(
        required=False,
        widget=forms.NumberInput(attrs={
            'placeholder': 'E.g.: 100',
            'class': 'form-control'
        })
    )
    
    class Meta:
        model = DeveloperProfile
        exclude = ['user']
    #def clean_phone(self):
    #    return validate_phone(self.cleaned_data.get('phone'))



