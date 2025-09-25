from django.contrib import admin
from .models import CustomUser, UploadBatch, UploadFile
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserAdminCreationForm, CustomUserAdminChangeForm
from .tasks import create_missing_developer_profiles
from apps.developers.models import DeveloperProfile
from apps.developers.models import DeveloperProfile
from django.db.models import Exists, OuterRef

# Register your models here.
@admin.action(description="Create developer profile")
def create_dev_profile_action(modeladmin, request, queryset):
    for user in queryset:

        create_missing_developer_profiles.delay(user.id)
            
            

class DeveloperProfileInline(admin.StackedInline):
    model = DeveloperProfile
    can_delete = False
    extra = 0
    classes = ('grp-collapse', 'grp-closed')  


class CustomUserAdmin(UserAdmin):
    add_form = CustomUserAdminCreationForm
    form = CustomUserAdminChangeForm
    model = CustomUser
    list_select_related = ("developerprofile",)  # evita N+1 si accedes user.profile

    list_display = [
        "email",
        "username",
        "first_name",
        "last_name",
        "timezone",
        "is_staff",
        "is_active",
        "role",
        "has_profile_display",
        "is_bootstrapped",
        "created_at",
    ]
    fieldsets = (
        (None, {"fields": ("username","email", "password", 'is_bootstrapped')}),
        ("Personal info", {"fields": ("first_name", "last_name", "timezone", "role")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    actions = [create_dev_profile_action]
    inlines = [DeveloperProfileInline]   # <- ahora sí aparece el perfil debajo del usuario
    def get_queryset(self, request):
            qs = super().get_queryset(request)
            # Anota si existe perfil (1 query eficiente)
            return qs.annotate(
                _has_profile=Exists(
                    DeveloperProfile.objects.filter(user_id=OuterRef("pk"))
                )
            )

    @admin.display(boolean=True, description="Has profile", ordering="_has_profile")
    def has_profile_display(self, obj):
            # Si ya vino con select_related('profile'), hasattr no hace query extra
            return getattr(obj, "_has_profile", hasattr(obj, "developerprofile"))



class UploadFileAdmin(admin.ModelAdmin):
    list_display = ("id", "number_file", "file", "status", "error_code", "batch", "created_at")
    list_filter = ("status", "created_at", "batch")
    search_fields = ("file", "error_code")
    ordering = ("-created_at",)

admin.site.register(CustomUser, CustomUserAdmin)
admin.site.register(UploadBatch)
admin.site.register(UploadFile, UploadFileAdmin)

    
"""

@admin.register(Magicktoken)
class MagicLinkAdmin(admin.ModelAdmin):
    list_display = ('token', 'created_at', 'used')
    readonly_fields = ('token', 'created_at', 'used')
    ordering = ('-created_at',)


"""



