from django.contrib import admin
from django.utils import timezone
from .models import Property, PropertyImage, PropertyVideo, PropertyAmenity, Booking, LandlordApplication


@admin.register(LandlordApplication)
class LandlordApplicationAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'phone', 'status', 'created_at', 'user']
    list_filter = ['status', 'created_at']
    search_fields = ['full_name', 'email', 'phone', 'user__username']
    readonly_fields = ['created_at', 'updated_at', 'user']
    
    fieldsets = (
        ('User Information', {
            'fields': ('user', 'full_name', 'email', 'phone')
        }),
        ('Location', {
            'fields': ('county', 'sub_county', 'estate', 'latitude', 'longitude'),
            'classes': ('collapse',)
        }),
        ('Verification', {
            'fields': ('id_document', 'status', 'review_notes')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_applications', 'reject_applications']
    
    def approve_applications(self, request, queryset):
        """Approve selected landlord applications"""
        updated = queryset.update(status='approved', review_notes='Approved by admin')
        self.message_user(request, f'{updated} application(s) approved successfully.')
    approve_applications.short_description = "Approve selected applications"
    
    def reject_applications(self, request, queryset):
        """Reject selected landlord applications"""
        updated = queryset.update(status='rejected', review_notes='Rejected by admin')
        self.message_user(request, f'{updated} application(s) rejected.')
    reject_applications.short_description = "Reject selected applications"


@admin.register(Property)
class PropertyAdmin(admin.ModelAdmin):
    list_display = ['name', 'property_type', 'price', 'verification_status', 'verification_score', 'ai_verification_result', 'available', 'owner', 'created_at']
    list_filter = ['property_type', 'verification_status', 'ai_verification_result', 'available', 'created_at']
    search_fields = ['name', 'description', 'owner__username']
    readonly_fields = ['created_at', 'updated_at', 'verified_at']
    
    fieldsets = (
        ('Basic Information', {
            'fields': ('owner', 'name', 'description', 'property_type', 'listing_type')
        }),
        ('Location', {
            'fields': ('estate', 'location_pin', 'county', 'sub_county', 'estate_name', 'street_address', 'landmark', 'latitude', 'longitude'),
            'classes': ('collapse',)
        }),
        ('Property Details', {
            'fields': ('bedrooms', 'bathrooms', 'square_feet', 'square_meters', 'price', 'deposit')
        }),
        ('Verification', {
            'fields': ('verification_status', 'verification_score', 'ai_verification_result', 'verified_at')
        }),
        ('Status', {
            'fields': ('available', 'available_from', 'featured', 'is_best_value')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )
    
    actions = ['approve_verification', 'reject_verification', 'mark_partial_match', 'mark_failed']
    
    def approve_verification(self, request, queryset):
        """Approve selected properties for verification"""
        updated = queryset.update(
            verification_status='approved',
            ai_verification_result='MATCH',
            verification_score=95,
            verified_at=timezone.now()
        )
        self.message_user(request, f'{updated} property/properties approved successfully.')
    approve_verification.short_description = "Approve verification for selected properties"
    
    def reject_verification(self, request, queryset):
        """Reject selected properties verification"""
        updated = queryset.update(
            verification_status='rejected',
            ai_verification_result='FAILED',
            verification_score=30,
            verified_at=timezone.now()
        )
        self.message_user(request, f'{updated} property/properties rejected.')
    reject_verification.short_description = "Reject verification for selected properties"
    
    def mark_partial_match(self, request, queryset):
        """Mark selected properties as partial match"""
        updated = queryset.update(
            verification_status='partial',
            ai_verification_result='PARTIAL',
            verification_score=65,
            verified_at=timezone.now()
        )
        self.message_user(request, f'{updated} property/properties marked as partial match.')
    mark_partial_match.short_description = "Mark as partial match"
    
    def mark_failed(self, request, queryset):
        """Mark selected properties as failed verification"""
        updated = queryset.update(
            verification_status='failed',
            ai_verification_result='FAILED',
            verification_score=20,
            verified_at=timezone.now()
        )
        self.message_user(request, f'{updated} property/properties marked as failed.')
    mark_failed.short_description = "Mark as failed verification"


@admin.register(Booking)
class BookingAdmin(admin.ModelAdmin):
    list_display = ['property', 'name', 'email', 'date', 'time_slot', 'status', 'created_at']
    list_filter = ['status', 'date', 'created_at']
    search_fields = ['name', 'email', 'phone', 'property__name']


admin.site.register(PropertyImage)
admin.site.register(PropertyVideo)
admin.site.register(PropertyAmenity)

