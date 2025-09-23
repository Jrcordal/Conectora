from django import forms
from django.core.exceptions import ValidationError
from .models import ClientProfile
from apps.developers.models import CURRENCY_CHOICES, validate_phone
from apps.users.forms import MultipleFileInput





class MultipleDocsUploadForm(forms.Form):
    files = forms.FileField(
        label="Relevant docs for the proposal",
        widget=MultipleFileInput(attrs={"accept": ".pdf,.docx"}),
        required=True,
        help_text="You can select several .pdf or .docx"
    )



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
    role_in_company = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'CEO, Founder, Project Manager',
            'class': 'form-control'
        })
    )

    class Meta:
        model = ClientProfile
        fields = [
            'telephone_number',
            'linkedin',
            'website',
            'currency',
            'role_in_company'
        ]



class IntakeForm(forms.ModelForm):
    client_description = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'We are an IT consulting company, We are a retail franchise...',
            'class':'form-control'
            })
            )
    problem = forms.CharField(
        required=False,
        widget = forms.TextInput(attrs= {
            'placeholder':'We need to develop a Machine Learning model to predict the amount of sales in the next quarter,We need to create a webapp to manage leads an distribute them to our franchisees...',
            'class':'form-control'
            })
            )
    end_user = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder':'The managers from the company, The franchisees and the headquarters...',
            'class':'form-control'
        })
    )

    end_goal = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Increase sales by 20% in Q4 by using the analytics dashboard, Improve lead management efficiency and avoid missclassification of leads...',
            'class':'form-control'
        })
    )

    must_features = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Dashboard with KPIs, Role-based access control, Mobile support...',
            'class':'form-control'
        })
    )

    required_workflows = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Lead assignment process, Approval workflow for discounts, Notification system...',
            'class':'form-control'
        })
    )

    must_not_do = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'Do not store sensitive customer data, Do not allow external access without login...',
            'class':'form-control'
        })
    )

    recommended_stack = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'React frontend, Django backend, PostgreSQL database, AWS hosting...',
            'class':'form-control'
        })
    )

    other_info = forms.CharField(
        required=False,
        widget=forms.TextInput(attrs={
            'placeholder': 'We already have a CRM in place, Budget is limited to $50k, Deadline is 6 months...',
            'class':'form-control'
        })
    )





