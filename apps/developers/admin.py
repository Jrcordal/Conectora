from django.contrib import admin, messages
from .models import DeveloperProfile, AuthorizedEmail
from .tasks import fill_developer_fields
from django.db.models import JSONField
import json

from django import forms

@admin.action(description="Upload fields from current CV")
def update_from_current_cv(modeladmin, request, queryset):
    ok = 0
    no_cv = 0
    for profile in queryset:
        if profile.cv_file:
            # La task espera user_id, no el pk del perfil
            fill_developer_fields.delay(profile.user_id)
            ok += 1
        else:
            no_cv += 1
    if ok:
        messages.success(request, f"{ok} tasks queued.")
    if no_cv:
        messages.warning(request, f"{no_cv} profiles did not have CV.")


class JSONTextarea(forms.Textarea):
    def format_value(self, value):
        try:
            return json.dumps(value, ensure_ascii=False, indent=2)
        except Exception:
            return value

@admin.register(DeveloperProfile) 
class DeveloperProfileAdmin(admin.ModelAdmin):
    # muestra columnas básicas (evita meter JSON enormes en la lista)
    list_display = ("user", "main_developer_role", "country_living_in", "nationality", "cv_file")
    search_fields = ("user__username", "user__email", "main_developer_role")
    list_filter = ("country_living_in", "nationality")
    autocomplete_fields = ["user"]
    actions = [update_from_current_cv]

    # Colapsables por secciones (Grappelli)
    fieldsets = (
        ("Identification", {
            "fields": ("user", "main_developer_role", "nationality"),
        }),
        ("Contact", {
            "classes": ("grp-collapse", "grp-open"),  # abierto por defecto
            "fields": ("telephone_number", "linkedin", "github", "personal_website"),
        }),
        ("Location", {
            "classes": ("grp-collapse", "grp-closed"),  # colapsado por defecto
            "fields": ("country_living_in",),
        }),
        ("Education", {
            "classes": ("grp-collapse", "grp-closed"),
            "fields": ("university_education", "education_certificates"),
        }),
        ("Experience / Proyects", {
            "classes": ("grp-collapse", "grp-closed"),
            "fields": ("experience", "projects", "volunteering"),
        }),
        ("Skills", {
            "classes": ("grp-collapse", "grp-closed"),
            "fields": (
                "programming_languages", "frameworks_libraries", "architectures_patterns",
                "tools_version_control", "databases", "cloud_platforms", "testing_qa",
                "devops_ci_cd", "containerization", "data_skills", "frontend_technologies",
                "mobile_development", "apis_integrations", "security", "agile_pm",
                "operating_systems",
            ),
        }),
        ("CV", {
            "classes": ("grp-collapse", "grp-open"),
            "fields": ("cv_file",),
        }),
    )

    # Widgets cómodos para JSON en la ficha
    formfield_overrides = {
        JSONField: {"widget": JSONTextarea(attrs={"rows": 12, "style": "font-family:monospace"})}
    }


@admin.register(AuthorizedEmail)
class AuthorizedEmailAdmin(admin.ModelAdmin):
    list_display = ("email", "active")
    search_fields = ("email",)
    list_filter = ("active",)