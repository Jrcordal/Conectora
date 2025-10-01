from django.contrib import admin
from .models import Project, Intake, AuthorizedClientEmail, ClientProfile

# Register your models here.



@admin.register(ClientProfile)
class ClientProfileAdmin(admin.ModelAdmin):
    list_display = ("user", "telephone_number", "linkedin", "website", "currency", "role_in_company", "number_of_projects", "total_candidates_matched", "search_limit")
    list_filter = ("currency", "role_in_company")
    search_fields = ("user__username", "user__email")
    autocomplete_fields = ("user",)

@admin.register(Project) 
class ProjectAdmin(admin.ModelAdmin):
    list_display = ("id", "client", "status", "matching_status", "matching_status_changed_at", "created_at", "updated_at", "processing_progress","proposal_draft", "tech_stack_draft", "team_recommendation", "potential_candidates_per_role", "selected_candidates")
    list_filter = ("status", "matching_status")
    search_fields = ("client__user__username", "client__user__email")
    autocomplete_fields = ("client",)

@admin.register(Intake) 
class IntakeAdmin(admin.ModelAdmin):
    list_display = ("id", "project", "client", "created_by", "created_at", "client_description", "problem", "end_user", "end_goal", "must_features", "required_workflows", "must_not_do", "recommended_stack", "other_info")
    list_filter = ("client", "created_by")
    search_fields = ("project__client__user__username", "project__client__user__email", "created_by__username", "created_by__email")
    autocomplete_fields = ("project", "client", "created_by")


@admin.register(AuthorizedClientEmail)
class AuthorizedEmailAdmin(admin.ModelAdmin):
    list_display = ("email", "active")
    search_fields = ("email",)
    list_filter = ("active",)