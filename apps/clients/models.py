from django.db import models
from django.conf import settings
from apps.developers.models import validate_phone,CURRENCY_CHOICES
from django.utils import timezone
from datetime import datetime
from django.core.exceptions import ValidationError
from apps.developers.models import CVStorage

# Create your models here.
class AuthorizedClientEmail(models.Model):
    email = models.EmailField(unique=True)
    active = models.BooleanField(default=True)


class ClientProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, primary_key=True,related_name='clientprofile')
    telephone_number = models.CharField(max_length=15, blank=True, validators=[validate_phone])
    linkedin = models.URLField(blank=True, null=True)
    website = models.URLField(blank=True, null=True)
    currency = models.CharField(max_length=3, choices=CURRENCY_CHOICES, blank=True, null=True)
    role_in_company = models.CharField(max_length=50, blank = True)
    number_of_projects = models.IntegerField(blank=True, default=0)
    total_candidates_matched = models.IntegerField(blank=True, default=0)
    search_limit = models.PositiveIntegerField(blank=True, default=3)
    
    def __str__(self):
        return self.user.username



class IntakeStage(models.TextChoices):
    INTAKE_REQUIREMENTS    = "intake_requirements",    "Requirements received"
    PROPOSAL_DRAFT   = "proposal_draft",  "AI-made proposal draft"
    TECH_STACK_DRAFT      = "tech_stack_draft",     "Created a tech stack draft"
    POTENTIAL_CANDIDATES     = "potential_candidates",    "Searched for potential candidates"
    SELECTED_CANDIDATES  = "selected_candidates", "Selected final candidates"



class ProjectStatus(models.TextChoices):
    AI_INTAKE          = "ai_intake", "AI Intake"
    PRESALE            = "presale", "Presale"
    CONTRACT_SIGNED    = "contract_signed", "Contract signed"
    CANCELLED_CONTRACT = "cancelled_contract", "Cancelled contract"
    COMPLETED          = "completed", "Completed"


class Project(models.Model):
    client = models.ForeignKey(ClientProfile, on_delete=models.CASCADE, related_name='clientproject')
    intake_requirements = models.JSONField(blank=True, null=True, default=None)
    proposal_draft = models.JSONField(blank=True,  null=True, default=None)
    tech_stack_draft = models.JSONField(blank=True,  null=True, default=None)
    potential_candidates = models.JSONField(blank=True,  null=True, default=None)
    selected_candidates = models.JSONField(blank=True,  null=True, default=None)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    status_intake = models.CharField(max_length=20, choices=IntakeStage.choices, default=IntakeStage.INTAKE_REQUIREMENTS)
    status_project = models.CharField(max_length=30, choices=ProjectStatus.choices, default=ProjectStatus.AI_INTAKE)


    def projects_in_month(self, year=None, month=None):
        if not year or not month:
            today = timezone.now()
            year, month = today.year, today.month
        return self.clientproject.filter(
            created_at__year=year,
            created_at__month=month
        ).count()



class Intake(models.Model):
    project = models.OneToOneField(Project, on_delete=models.CASCADE, related_name="intake")
    client_description = models.TextField(blank=True, null=True)
    problem = models.TextField(blank=True, null=True)
    end_user = models.TextField(blank=True, null=True)
    end_goal = models.TextField(blank=True, null=True)
    must_features = models.TextField(blank=True, null=True)
    required_workflows = models.TextField(blank=True, null=True)
    must_not_do = models.TextField(blank=True, null=True)
    recommended_stack = models.TextField(blank=True, null=True)
    other_info = models.TextField(blank=True, null=True)


    def __str__(self):
        return f"Intake for Project #{self.project_id}"



def intake_upload_path(instance, filename):
    timestamp = datetime.now().strftime("%Y%m%d-%H%M%S")
    if filename.endswith('.pdf'):
        return f"intake/{instance.user.id}/{timestamp}.pdf"  # ya no pones 'cvs/' porque lo pone storage
    elif filename.endswith('.docx'):
        return f"intake/{instance.user.id}/{timestamp}.docx"  # ya no pones 'cvs/' porque lo pone storage
    else:
        raise ValidationError("Only PDF and DOCX files are allowed.")


class Document(models.Model):
    intake = models.ForeignKey(Intake, on_delete=models.CASCADE, related_name="documents")
    file = models.FileField(upload_to=intake_upload_path, blank=False, null = False, storage=CVStorage())
    original_name = models.CharField(max_length=255, blank=True)
    size_bytes = models.BigIntegerField(blank=True, null=True)
    pages = models.IntegerField(blank=True, null=True)
    extracted_text = models.TextField(blank=True, null=True)
    created_at = models.DateTimeField(auto_now_add=True)    



