from django.db import models
from django.conf import settings
from apps.developers.models import validate_phone,CURRENCY_CHOICES
from django.utils import timezone
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
