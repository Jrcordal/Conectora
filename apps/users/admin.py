from django.contrib import admin
from .models import CustomUser
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserAdminCreationForm, CustomUserAdminChangeForm
from .tasks import create_missing_developer_profiles

# Register your models here.

def create_dev_profile_action(modeladmin, request, queryset):
    for user in queryset:

        create_missing_developer_profiles.delay(user.id)
            
            




class CustomUserAdmin(UserAdmin):
    add_form = CustomUserAdminCreationForm
    form = CustomUserAdminChangeForm
    model = CustomUser
    list_display = [
        "email",
        "username",
        "first_name",
        "last_name",
        "timezone",
        "is_staff",
        "is_active",
        "role",
    ]
    fieldsets = (
        (None, {"fields": ("email", "password")}),
        ("Personal info", {"fields": ("first_name", "last_name", "timezone", "role")}),
        ("Permissions", {"fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions")}),
        ("Important dates", {"fields": ("last_login", "date_joined")}),
    )
    actions = [create_dev_profile_action]




admin.site.register(CustomUser, CustomUserAdmin)

    
"""

@admin.register(Magicktoken)
class MagicLinkAdmin(admin.ModelAdmin):
    list_display = ('token', 'created_at', 'used')
    readonly_fields = ('token', 'created_at', 'used')
    ordering = ('-created_at',)


"""



