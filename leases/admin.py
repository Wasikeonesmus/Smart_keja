from django.contrib import admin
from .models import Lease, LeaseAmendment, DocumentVault, LeaseReminder


@admin.register(Lease)
class LeaseAdmin(admin.ModelAdmin):
    list_display = ['lease_number', 'property', 'landlord', 'tenant', 'lease_type', 'start_date', 'end_date', 'monthly_rent', 'status', 'created_at']
    list_filter = ['status', 'lease_type', 'start_date', 'end_date']
    search_fields = ['lease_number', 'property__name', 'landlord__username', 'tenant__username']
    raw_id_fields = ['property', 'landlord', 'tenant']
    date_hierarchy = 'start_date'
    readonly_fields = ['lease_number', 'created_at', 'updated_at', 'signed_at', 'activated_at']


@admin.register(LeaseAmendment)
class LeaseAmendmentAdmin(admin.ModelAdmin):
    list_display = ['lease', 'amendment_type', 'effective_date', 'landlord_signed', 'tenant_signed', 'created_at']
    list_filter = ['amendment_type', 'effective_date', 'landlord_signed', 'tenant_signed']
    search_fields = ['lease__lease_number', 'description']
    raw_id_fields = ['lease']


@admin.register(DocumentVault)
class DocumentVaultAdmin(admin.ModelAdmin):
    list_display = ['title', 'document_type', 'uploaded_by', 'property', 'access_level', 'created_at']
    list_filter = ['document_type', 'access_level', 'created_at']
    search_fields = ['title', 'description', 'uploaded_by__username', 'property__name']
    raw_id_fields = ['uploaded_by', 'property', 'lease']
    filter_horizontal = ['shared_with']


@admin.register(LeaseReminder)
class LeaseReminderAdmin(admin.ModelAdmin):
    list_display = ['lease', 'reminder_type', 'reminder_date', 'sent_to_landlord', 'sent_to_tenant', 'sent_at']
    list_filter = ['reminder_type', 'reminder_date', 'sent_to_landlord', 'sent_to_tenant']
    search_fields = ['lease__lease_number', 'message']
    raw_id_fields = ['lease']
    date_hierarchy = 'reminder_date'
