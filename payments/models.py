"""
Payment System for SmartKeja
Handles M-Pesa STK Push, payment processing, and payouts
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal


class Payment(models.Model):
    """Payment record for various payment types"""
    
    PAYMENT_TYPES = [
        ('rent', 'Rent Payment'),
        ('deposit', 'Deposit'),
        ('booking', 'Booking Payment'),
        ('airbnb', 'Airbnb Booking'),
        ('maintenance', 'Maintenance Fee'),
        ('subscription', 'Subscription'),
        ('featured_listing', 'Featured Listing'),
        ('commission', 'Commission'),
        ('payout', 'Payout'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    PAYMENT_METHODS = [
        ('mpesa_stk', 'M-Pesa STK Push'),
        ('mpesa_paybill', 'M-Pesa Paybill'),
        ('bank_transfer', 'Bank Transfer'),
        ('card', 'Card'),
        ('wallet', 'Wallet'),
    ]
    
    # User and payment details
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payments')
    payment_type = models.CharField(max_length=20, choices=PAYMENT_TYPES)
    
    # Amount
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    currency = models.CharField(max_length=3, default='KES')
    
    # Payment method
    payment_method = models.CharField(max_length=20, choices=PAYMENT_METHODS, default='mpesa_stk')
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # M-Pesa STK Push details
    mpesa_checkout_request_id = models.CharField(max_length=100, blank=True)
    mpesa_merchant_request_id = models.CharField(max_length=100, blank=True)
    mpesa_receipt_number = models.CharField(max_length=50, blank=True)
    mpesa_phone_number = models.CharField(max_length=20, blank=True)
    mpesa_result_code = models.CharField(max_length=10, blank=True)
    mpesa_result_desc = models.TextField(blank=True)
    
    # References
    reference = models.CharField(max_length=200, blank=True)  # External reference (e.g., booking ID)
    description = models.TextField(blank=True)
    
    # Partial payments (for rent deposits, etc.)
    is_partial = models.BooleanField(default=False)
    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        null=True,
        blank=True
    )  # Total amount if partial payment
    
    # Fees
    platform_fee = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )
    transaction_fee = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    # Receipt
    receipt_generated = models.BooleanField(default=False)
    receipt_file = models.FileField(upload_to='receipts/', null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['payment_type']),
            models.Index(fields=['mpesa_checkout_request_id']),
        ]
    
    def __str__(self):
        return f"{self.get_payment_type_display()} - KES {self.amount} ({self.status})"
    
    @property
    def total_paid(self):
        """Total amount including fees"""
        return self.amount + self.platform_fee + self.transaction_fee


class Payout(models.Model):
    """Payout to landlords, hosts, agents, etc."""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('processing', 'Processing'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    PAYOUT_METHODS = [
        ('mpesa', 'M-Pesa'),
        ('bank_transfer', 'Bank Transfer'),
        ('wallet', 'Wallet'),
    ]
    
    # Recipient
    recipient = models.ForeignKey(User, on_delete=models.CASCADE, related_name='payouts')
    
    # Amount
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.01'))]
    )
    currency = models.CharField(max_length=3, default='KES')
    
    # Payout method
    payout_method = models.CharField(max_length=20, choices=PAYOUT_METHODS, default='mpesa')
    
    # Bank details (if bank transfer)
    bank_name = models.CharField(max_length=100, blank=True)
    account_number = models.CharField(max_length=50, blank=True)
    account_name = models.CharField(max_length=200, blank=True)
    
    # M-Pesa details
    mpesa_phone_number = models.CharField(max_length=20, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Reference
    reference = models.CharField(max_length=200, blank=True)
    description = models.TextField(blank=True)
    
    # Fees
    processing_fee = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00')
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    processed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Payout to {self.recipient.username} - KES {self.amount} ({self.status})"

