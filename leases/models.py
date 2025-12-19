"""
Digital Leases & Documents System for SmartKeja
Handles lease generation, e-signatures, and document management
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
from properties.models import Property
from datetime import timedelta
from django.utils import timezone


class Lease(models.Model):
    """Digital lease agreements"""
    
    STATUS_CHOICES = [
        ('draft', 'Draft'),
        ('pending_signature', 'Pending Signature'),
        ('signed', 'Signed'),
        ('active', 'Active'),
        ('expired', 'Expired'),
        ('terminated', 'Terminated'),
        ('cancelled', 'Cancelled'),
    ]
    
    LEASE_TYPES = [
        ('residential', 'Residential Lease'),
        ('commercial', 'Commercial Lease'),
        ('short_term', 'Short-Term Lease'),
        ('month_to_month', 'Month-to-Month'),
    ]
    
    # Parties
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='leases')
    landlord = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='landlord_leases',
        help_text="Property owner/landlord"
    )
    tenant = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='tenant_leases'
    )
    
    # Lease details
    lease_type = models.CharField(max_length=20, choices=LEASE_TYPES, default='residential')
    lease_number = models.CharField(max_length=50, unique=True, blank=True)
    
    # Term
    start_date = models.DateField()
    end_date = models.DateField()
    duration_months = models.IntegerField(validators=[MinValueValidator(1)])
    
    # Rent
    monthly_rent = models.DecimalField(max_digits=10, decimal_places=2, validators=[MinValueValidator(Decimal('0.01'))])
    security_deposit = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    currency = models.CharField(max_length=3, default='KES')
    
    # Terms and conditions
    terms = models.TextField(help_text="Lease terms and conditions")
    special_clauses = models.TextField(blank=True)
    
    # Renewal
    auto_renewal = models.BooleanField(default=False)
    renewal_notice_days = models.IntegerField(default=30)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='draft')
    
    # Signatures
    landlord_signed = models.BooleanField(default=False)
    tenant_signed = models.BooleanField(default=False)
    landlord_signature = models.TextField(blank=True)  # Base64 encoded signature
    tenant_signature = models.TextField(blank=True)
    landlord_signed_at = models.DateTimeField(null=True, blank=True)
    tenant_signed_at = models.DateTimeField(null=True, blank=True)
    
    # Document
    lease_document = models.FileField(upload_to='leases/documents/', null=True, blank=True)
    lease_pdf = models.FileField(upload_to='leases/pdfs/', null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    signed_at = models.DateTimeField(null=True, blank=True)
    activated_at = models.DateTimeField(null=True, blank=True)
    expired_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['property', 'status']),
            models.Index(fields=['landlord', 'status']),
            models.Index(fields=['tenant', 'status']),
            models.Index(fields=['start_date', 'end_date']),
        ]
    
    def __str__(self):
        return f"Lease #{self.lease_number} - {self.property.name} ({self.status})"
    
    def save(self, *args, **kwargs):
        if not self.lease_number:
            # Generate lease number
            from datetime import datetime
            self.lease_number = f"LSE-{datetime.now().strftime('%Y%m%d')}-{self.id or 'NEW'}"
        
        # Calculate duration if not set
        if self.start_date and self.end_date and not self.duration_months:
            delta = self.end_date - self.start_date
            self.duration_months = max(1, delta.days // 30)
        
        super().save(*args, **kwargs)
    
    def is_currently_active(self):
        """Check if lease is currently active"""
        today = timezone.now().date()
        return (
            self.status == 'active' and
            self.start_date <= today <= self.end_date
        )
    
    def get_days_until_expiry(self):
        """Days until lease expires"""
        if not self.end_date:
            return None
        delta = self.end_date - timezone.now().date()
        return delta.days
    
    def is_fully_signed(self):
        """Check if both parties have signed"""
        return self.landlord_signed and self.tenant_signed


class LeaseAmendment(models.Model):
    """Amendments/modifications to existing leases"""
    lease = models.ForeignKey(Lease, on_delete=models.CASCADE, related_name='amendments')
    
    amendment_type = models.CharField(
        max_length=20,
        choices=[
            ('rent_change', 'Rent Change'),
            ('term_extension', 'Term Extension'),
            ('term_reduction', 'Term Reduction'),
            ('add_tenant', 'Add Tenant'),
            ('remove_tenant', 'Remove Tenant'),
            ('other', 'Other'),
        ]
    )
    
    description = models.TextField()
    effective_date = models.DateField()
    
    # Signatures
    landlord_signed = models.BooleanField(default=False)
    tenant_signed = models.BooleanField(default=False)
    landlord_signature = models.TextField(blank=True)
    tenant_signature = models.TextField(blank=True)
    
    amendment_document = models.FileField(upload_to='leases/amendments/', null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    signed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Amendment to {self.lease.lease_number} - {self.get_amendment_type_display()}"


class DocumentVault(models.Model):
    """Secure document vault for storing property-related documents"""
    
    DOCUMENT_TYPES = [
        ('lease', 'Lease Agreement'),
        ('title_deed', 'Title Deed'),
        ('id', 'ID Document'),
        ('kra_pin', 'KRA PIN Certificate'),
        ('utility_bill', 'Utility Bill'),
        ('inspection_report', 'Inspection Report'),
        ('maintenance_report', 'Maintenance Report'),
        ('receipt', 'Receipt'),
        ('invoice', 'Invoice'),
        ('contract', 'Contract'),
        ('other', 'Other'),
    ]
    
    # Ownership
    uploaded_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='uploaded_documents')
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='documents',
        null=True,
        blank=True
    )
    lease = models.ForeignKey(
        Lease,
        on_delete=models.CASCADE,
        related_name='documents',
        null=True,
        blank=True
    )
    
    # Document details
    document_type = models.CharField(max_length=20, choices=DOCUMENT_TYPES)
    title = models.CharField(max_length=200)
    description = models.TextField(blank=True)
    
    # File
    document_file = models.FileField(upload_to='documents/vault/')
    file_size = models.IntegerField(null=True, blank=True)  # Size in bytes
    mime_type = models.CharField(max_length=100, blank=True)
    
    # Security
    is_encrypted = models.BooleanField(default=False)
    access_level = models.CharField(
        max_length=20,
        choices=[
            ('private', 'Private'),
            ('shared', 'Shared'),
            ('public', 'Public'),
        ],
        default='private'
    )
    
    # Sharing
    shared_with = models.ManyToManyField(User, related_name='shared_documents', blank=True)
    
    # Expiry
    expires_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['uploaded_by', 'document_type']),
            models.Index(fields=['property', 'document_type']),
        ]
    
    def __str__(self):
        return f"{self.title} ({self.get_document_type_display()})"
    
    def check_is_expired(self):
        """Check if document has expired"""
        if not self.expires_at:
            return False
        return timezone.now() > self.expires_at


class LeaseReminder(models.Model):
    """Reminders for lease-related events"""
    lease = models.ForeignKey(Lease, on_delete=models.CASCADE, related_name='reminders')
    
    reminder_type = models.CharField(
        max_length=20,
        choices=[
            ('expiry', 'Lease Expiry'),
            ('renewal', 'Renewal Notice'),
            ('rent_due', 'Rent Due'),
            ('inspection', 'Inspection Due'),
            ('custom', 'Custom'),
        ]
    )
    
    reminder_date = models.DateField()
    message = models.TextField()
    
    # Notification
    sent_to_landlord = models.BooleanField(default=False)
    sent_to_tenant = models.BooleanField(default=False)
    sent_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['reminder_date']
    
    def __str__(self):
        return f"Reminder for {self.lease.lease_number} - {self.get_reminder_type_display()}"
