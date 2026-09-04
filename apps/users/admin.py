from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin

from .models import Department, User


@admin.register(Department)
class DepartmentAdmin(admin.ModelAdmin):
    list_display = ('name',)
    search_fields = ('name',)


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ('username', 'first_name', 'last_name', 'department', 'is_md', 'is_gm', 'is_staff')
    list_filter = ('department', 'is_md', 'is_gm', 'is_staff', 'is_active')
    fieldsets = BaseUserAdmin.fieldsets + (
        ('ERP Profile', {'fields': ('department', 'phone', 'is_md', 'is_gm')}),
    )
