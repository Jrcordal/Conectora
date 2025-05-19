from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
import phonenumbers
from django.core.exceptions import ValidationError
from apps.users.models import Profile


#def validate_phone(value):
#    try:
#        phone_number = phonenumbers.parse(str(value))
#    except phonenumbers.phonenumberutil.NumberParseException:
#        raise ValidationError("Invalid phone number format. Please include country code (e.g. +31)")
#    if not phonenumbers.is_valid_number(phone_number):
#        raise ValidationError("This is not a valid phone number")
#    return phonenumbers.format_number(phone_number, phonenumbers.PhoneNumberFormat.E164)
   

class RegisterForm(UserCreationForm):
    email = forms.EmailField()
    #phone = forms.CharField(max_length=15)
    class Meta: # Meta class holds information about RegisterForm class
        model = User
        fields = ['username','first_name','last_name','email','password1','password2']
    def clean_email(self):
        email = self.cleaned_data.get('email')
        if User.objects.filter(email=email).exists():
            raise forms.ValidationError("This email address is already in use.")
        return email
    def clean(self):
        cleaned_data = super().clean()
        first_name = cleaned_data.get('first_name')
        last_name = cleaned_data.get('last_name')
        
        if not first_name:
            raise forms.ValidationError('First name is mandatory')
        if not last_name:
            raise forms.ValidationError('Last name is mandatory')
            
        return cleaned_data
    #def clean_phone(self):
    #    return validate_phone(self.cleaned_data.get('phone'))



            
class ProfileForm(forms.ModelForm):
    # Define fields with appropriate widgets and placeholders
    university_education = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'placeholder': 'List your university education (one per line)\nE.g.:\nBS Computer Science, MIT, 2015-2019\nMS Data Science, Stanford, 2019-2021',
            'rows': 4,
            'class': 'form-control'
        })
    )
    
    education_certificates = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'placeholder': 'List your certificates (one per line)\nE.g.:\nAWS Certified Solutions Architect, 2022\nGoogle Cloud Professional Data Engineer, 2021',
            'rows': 4,
            'class': 'form-control'
        })
    )
    
    experience = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'placeholder': 'List your work experience (one per line)\nE.g.:\nSoftware Engineer, Google, 2019-2021\nData Scientist, Microsoft, 2021-Present',
            'rows': 4,
            'class': 'form-control'
        })
    )
    
    skills = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'placeholder': 'List your skills (one per line)\nE.g.:\nPython\nJavaScript\nData Analysis\nMachine Learning',
            'rows': 6,
            'class': 'form-control'
        })
    )
    
    projects = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'placeholder': 'List your projects (one per line)\nE.g.:\nCV Management System - Django web application\nData Visualization Dashboard - React',
            'rows': 4,
            'class': 'form-control'
        })
    )
    
    interests = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'placeholder': 'List your interests (one per line)\nE.g.:\nArtificial Intelligence\nWeb Development\nCryptography',
            'rows': 5,
            'class': 'form-control'
        })
    )
    
    volunteering = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'placeholder': 'List your volunteering experiences (one per line)\nE.g.:\nTech mentor at local school, 2020-Present\nOpen source contributor, React project',
            'rows': 4,
            'class': 'form-control'
        })
    )
    
    languages = forms.CharField(
        required=False,
        widget=forms.Textarea(attrs={
            'placeholder': 'List languages you speak (one per line)\nE.g.:\nEnglish (Native)',
            'rows': 4,
            'class': 'form-control'
        })
    )
    
    location = forms.CharField(
        max_length=100,
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'E.g.: San Francisco, CA',
            'class': 'form-control'
        })
    )
    
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
        model = Profile
        exclude = ['user']
    #def clean_phone(self):
    #    return validate_phone(self.cleaned_data.get('phone'))