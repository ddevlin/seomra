from django.contrib import admin

from .models import MagicLink, User


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ("email", "role", "is_active", "date_joined")
    list_filter = ("role",)
    search_fields = ("email",)


@admin.register(MagicLink)
class MagicLinkAdmin(admin.ModelAdmin):
    list_display = ("user", "created_at", "used_at")
