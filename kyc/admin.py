from django.contrib import admin
from .models import KYCVerification, VerificationBadge


@admin.register(KYCVerification)
class KYCVerificationAdmin(admin.ModelAdmin):
    list_display = ['user', 'role_type', 'verification_level', 'status', 'verification_score', 'created_at']
    list_filter = ['status', 'verification_level', 'role_type']
    search_fields = ['user__username', 'kra_pin_number', 'title_deed_number']
    raw_id_fields = ['user', 'reviewed_by']
    readonly_fields = ['created_at', 'updated_at', 'verification_score']


@admin.register(VerificationBadge)
class VerificationBadgeAdmin(admin.ModelAdmin):
    list_display = ['user', 'badge_type', 'is_active', 'issued_at', 'expires_at']
    list_filter = ['badge_type', 'is_active']
    search_fields = ['user__username']
    raw_id_fields = ['user']

