from django import forms
from django.core.exceptions import ValidationError
from .models import ClientProfile
from apps.developers.models import CURRENCY_CHOICES, validate_phone
import os


class ClientProfileForm(forms.ModelForm):
    telephone_number = forms.CharField(
        required=False,
        validators=[validate_phone],  # <-- Añadir el validador aquí
        widget=forms.TextInput(attrs={
            'placeholder': 'E.g.: +31 6 12345678',
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

    website = forms.URLField(
        required=False,
        widget=forms.URLInput(attrs={
            'placeholder': 'E.g.: https://yourpersonalwebsite.com',
            'class': 'form-control'
        })
    )
    currency = forms.ChoiceField(
        required=False,
        choices=CURRENCY_CHOICES,
        widget=forms.Select(attrs={'class': 'form-control'})
    )


    class Meta:
        model = ClientProfile
        fields = [
            'telephone_number',
            'linkedin',
            'website',
            'currency'
        ]





