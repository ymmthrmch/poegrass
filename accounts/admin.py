from .models import User
from django.contrib import admin

class UserAdmin(admin.ModelAdmin):
    fields=[
        "account_id",
        "first_name",
        "last_name",
        "email",
    ]

admin.site.register(User, UserAdmin)