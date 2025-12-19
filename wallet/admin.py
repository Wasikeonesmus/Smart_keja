from django.contrib import admin
from .models import Wallet, Transaction, PaymentStatement


@admin.register(Wallet)
class WalletAdmin(admin.ModelAdmin):
    list_display = ['user', 'balance', 'credit_score', 'is_active', 'is_verified', 'created_at']
    list_filter = ['is_active', 'is_verified']
    search_fields = ['user__username', 'user__email']
    raw_id_fields = ['user']
    readonly_fields = ['created_at', 'updated_at']


@admin.register(Transaction)
class TransactionAdmin(admin.ModelAdmin):
    list_display = ['wallet', 'transaction_type', 'amount', 'status', 'payment_method', 'created_at']
    list_filter = ['status', 'transaction_type', 'payment_method']
    search_fields = ['wallet__user__username', 'mpesa_receipt_number', 'reference']
    raw_id_fields = ['wallet']
    readonly_fields = ['created_at']


@admin.register(PaymentStatement)
class PaymentStatementAdmin(admin.ModelAdmin):
    list_display = ['wallet', 'start_date', 'end_date', 'opening_balance', 'closing_balance', 'created_at']
    list_filter = ['start_date', 'end_date']
    search_fields = ['wallet__user__username']
    raw_id_fields = ['wallet']

