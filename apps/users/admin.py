from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from apps.users import models

# Register your models here.
class UserAdmin(BaseUserAdmin):
    pass

admin.site.register(models.User, UserAdmin)
