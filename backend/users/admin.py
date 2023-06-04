from django.contrib import admin
from django.contrib.auth.admin import UserAdmin

from .models import Subscription, User

admin.site.register(User, UserAdmin)


class SubscriptionAdmin(admin.ModelAdmin):
    list_display = ("author", "user")
    search_fields = ("author", "user")
    list_filter = ("author", "user")
    empty_value_display = "-empty-"


admin.site.register(Subscription, SubscriptionAdmin)
