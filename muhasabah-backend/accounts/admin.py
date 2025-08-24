from django.contrib import admin

# Register your models here
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import User

@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ('-date_joined',)
    list_display = ('email','username','role','location','whatsapp','is_active','is_staff','date_joined')
    search_fields = ('email','username','whatsapp')
    fieldsets = (
        (None, {'fields': ('email','username','password')}),
        ('Profile', {'fields': ('role','location','whatsapp')}),
        ('Permissions', {'fields': ('is_active','is_staff','is_superuser','groups','user_permissions')}),
        ('Important dates', {'fields': ('last_login','date_joined')}),
    )
    add_fieldsets = (
        (None, {'classes': ('wide',),
                'fields': ('email','username','role','location','whatsapp','password1','password2')}),
    )
