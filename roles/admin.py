from django.contrib import admin
from .models import UserRole, RoleSession


@admin.register(UserRole)
class UserRoleAdmin(admin.ModelAdmin):
    list_display = ['user', 'role_type', 'is_active', 'is_primary', 'created_at']
    list_filter = ['role_type', 'is_active', 'is_primary']
    search_fields = ['user__username', 'user__email']
    raw_id_fields = ['user']


@admin.register(RoleSession)
class RoleSessionAdmin(admin.ModelAdmin):
    list_display = ['user', 'current_role', 'last_switched_at']
    search_fields = ['user__username']
    raw_id_fields = ['user', 'current_role']

