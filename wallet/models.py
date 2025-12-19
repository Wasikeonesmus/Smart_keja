"""
Wallet System for SmartKeja
Handles user wallets, transactions, credit scores, and payment history
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal


class Wallet(models.Model):
    """User wallet for storing balance and payment history"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='wallet')
    
    # Balance
    balance = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=Decimal('0.00'),
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    
    # Credit Score (0-1000)
    credit_score = models.IntegerField(
        default=500,
        validators=[MinValueValidator(0)]
    )
    
    # Status
    is_active = models.BooleanField(default=True)
    is_verified = models.BooleanField(default=False)  # KYC verified wallet
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Wallet for {self.user.username} - KES {self.balance}"
    
    def add_funds(self, amount, transaction_type='deposit', reference=None):
        """Add funds to wallet"""
        if amount <= 0:
            raise ValueError("Amount must be positive")
        
        self.balance += Decimal(str(amount))
        self.save()
        
        # Create transaction record
        Transaction.objects.create(
            wallet=self,
            transaction_type=transaction_type,
            amount=amount,
            balance_after=self.balance,
            reference=reference
        )
        
        return self.balance
    
    def deduct_funds(self, amount, transaction_type='payment', reference=None):
        """Deduct funds from wallet"""
        if amount <= 0:
            raise ValueError("Amount must be positive")
        
        if self.balance < amount:
            raise ValueError("Insufficient balance")
        
        self.balance -= Decimal(str(amount))
        self.save()
        
        # Create transaction record
        Transaction.objects.create(
            wallet=self,
            transaction_type=transaction_type,
            amount=-amount,  # Negative for deduction
            balance_after=self.balance,
            reference=reference
        )
        
        return self.balance


class Transaction(models.Model):
    """Transaction record for wallet operations"""
    
    TRANSACTION_TYPES = [
        ('deposit', 'Deposit'),
        ('withdrawal', 'Withdrawal'),
        ('payment', 'Payment'),
        ('refund', 'Refund'),
        ('commission', 'Commission'),
        ('rent_payment', 'Rent Payment'),
        ('booking_payment', 'Booking Payment'),
        ('airbnb_payment', 'Airbnb Payment'),
        ('payout', 'Payout'),
        ('fee', 'Fee'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
    ]
    
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='transactions')
    
    # Transaction details
    transaction_type = models.CharField(max_length=20, choices=TRANSACTION_TYPES)
    amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    balance_after = models.DecimalField(max_digits=12, decimal_places=2)
    
    # Payment method
    payment_method = models.CharField(
        max_length=20,
        choices=[
            ('mpesa', 'M-Pesa'),
            ('bank_transfer', 'Bank Transfer'),
            ('card', 'Card'),
            ('wallet', 'Wallet'),
            ('cash', 'Cash'),
        ],
        default='mpesa'
    )
    
    # M-Pesa specific
    mpesa_receipt_number = models.CharField(max_length=50, blank=True)
    mpesa_phone_number = models.CharField(max_length=20, blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # References
    reference = models.CharField(max_length=200, blank=True)  # External reference
    description = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['wallet', 'created_at']),
            models.Index(fields=['status']),
            models.Index(fields=['transaction_type']),
        ]
    
    def __str__(self):
        return f"{self.get_transaction_type_display()} - KES {self.amount} ({self.status})"


class PaymentStatement(models.Model):
    """PDF statements for wallet transactions"""
    wallet = models.ForeignKey(Wallet, on_delete=models.CASCADE, related_name='statements')
    
    # Statement period
    start_date = models.DateField()
    end_date = models.DateField()
    
    # Statement file
    pdf_file = models.FileField(upload_to='statements/', null=True, blank=True)
    
    # Summary
    opening_balance = models.DecimalField(max_digits=12, decimal_places=2)
    closing_balance = models.DecimalField(max_digits=12, decimal_places=2)
    total_debits = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    total_credits = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-end_date']
    
    def __str__(self):
        return f"Statement for {self.wallet.user.username} - {self.start_date} to {self.end_date}"

