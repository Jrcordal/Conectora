from django.contrib import admin
from .models import DeveloperProfile, AuthorizedEmail

@admin.register(DeveloperProfile)
class DeveloperProfileAdmin(admin.ModelAdmin):
    list_display = [field.name for field in DeveloperProfile._meta.fields]
    search_fields = ("user__username", "main_developer_role", "country")

@admin.register(AuthorizedEmail)
class AuthorizedEmailAdmin(admin.ModelAdmin):
    list_display = ("email", "active")
    search_fields = ("email",)
    list_filter = ("active",)