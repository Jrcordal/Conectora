from django.contrib import admin, messages
from .models import DeveloperProfile, AuthorizedEmail
from .tasks import fill_developer_fields


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
        messages.success(request, f"Se encolaron {ok} tareas.")
    if no_cv:
        messages.warning(request, f"{no_cv} perfiles no tenían CV.")



@admin.register(DeveloperProfile)
class DeveloperProfileAdmin(admin.ModelAdmin):
    list_display = [field.name for field in DeveloperProfile._meta.fields]
    search_fields = ("user__username", "main_developer_role", "country")
    actions = [update_from_current_cv]



@admin.register(AuthorizedEmail)
class AuthorizedEmailAdmin(admin.ModelAdmin):
    list_display = ("email", "active")
    search_fields = ("email",)
    list_filter = ("active",)