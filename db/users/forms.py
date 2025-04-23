from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
import phonenumbers
from django.core.exceptions import ValidationError
from users.models import Profile


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
        fields = ['username','email','password1','password2']
    #def clean_phone(self):
    #    return validate_phone(self.cleaned_data.get('phone'))



            
class ProfileForm(forms.ModelForm): # Use of ModelForm to create a form from a model because using only a model does not allow to show the validation errors to the user
    class Meta:
        model = Profile
        exclude = ['user']
    #def clean_phone(self):
    #    return validate_phone(self.cleaned_data.get('phone'))







