from django.contrib import admin
from .models import Profile, MagicLink

# Register your models here.

admin.site.register(Profile)


@admin.register(MagicLink)
class MagicLinkAdmin(admin.ModelAdmin):
    list_display = ('token', 'created_at', 'used')
    readonly_fields = ('token', 'created_at', 'used')
    ordering = ('-created_at',)





