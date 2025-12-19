from django.contrib import admin
from .models import Payment, Payout


@admin.register(Payment)
class PaymentAdmin(admin.ModelAdmin):
    list_display = ['user', 'payment_type', 'amount', 'status', 'payment_method', 'created_at']
    list_filter = ['status', 'payment_type', 'payment_method']
    search_fields = ['user__username', 'mpesa_receipt_number', 'reference', 'mpesa_checkout_request_id']
    raw_id_fields = ['user']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Payout)
class PayoutAdmin(admin.ModelAdmin):
    list_display = ['recipient', 'amount', 'status', 'payout_method', 'created_at']
    list_filter = ['status', 'payout_method']
    search_fields = ['recipient__username', 'reference', 'mpesa_phone_number']
    raw_id_fields = ['recipient']

