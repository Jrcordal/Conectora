from django.contrib import admin
from .models import CustomUser
from django.contrib.auth.admin import UserAdmin
from .forms import CustomUserAdminCreationForm, CustomUserAdminChangeForm

# Register your models here.

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




admin.site.register(CustomUser, CustomUserAdmin)


"""

@admin.register(Magicktoken)
class MagicLinkAdmin(admin.ModelAdmin):
    list_display = ('token', 'created_at', 'used')
    readonly_fields = ('token', 'created_at', 'used')
    ordering = ('-created_at',)


"""



