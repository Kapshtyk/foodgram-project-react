from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Subscription, User


class UserAdmin(UserAdmin):
    list_display = (
        "username",
        "email",
        "first_name",
        "last_name",
        "is_staff",
        "is_active",
    )
    search_fields = ("username", "email", "first_name", "last_name")
    list_filter = ("email", "first_name", "last_name")
    empty_value_display = "-empty-"


admin.site.register(User, UserAdmin)


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("author", "user")
    search_fields = ("author", "user")
    list_filter = ("author", "user")
    empty_value_display = "-empty-"


admin.site.register(Subscription, SubscriptionAdmin)
