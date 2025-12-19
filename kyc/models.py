"""
KYC (Know Your Customer) verification system
Handles ID verification, KRA PIN, face matching, and title deed verification
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class KYCVerification(models.Model):
    """KYC verification record for a user in a specific role"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('under_review', 'Under Review'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('expired', 'Expired'),
    ]
    
    VERIFICATION_LEVEL_CHOICES = [
        ('basic', 'Basic'),  # ID only
        ('standard', 'Standard'),  # ID + KRA PIN
        ('advanced', 'Advanced'),  # ID + KRA PIN + Face Match
        ('premium', 'Premium'),  # All + Title Deed (for landlords/sellers)
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='kyc_verifications')
    role_type = models.CharField(max_length=20)  # Matches UserRole.ROLE_CHOICES
    
    # Verification Level
    verification_level = models.CharField(
        max_length=20,
        choices=VERIFICATION_LEVEL_CHOICES,
        default='basic'
    )
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    verification_score = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    # Documents
    id_document_front = models.FileField(upload_to='kyc/ids/front/', null=True, blank=True)
    id_document_back = models.FileField(upload_to='kyc/ids/back/', null=True, blank=True)
    kra_pin_document = models.FileField(upload_to='kyc/kra/', null=True, blank=True)
    title_deed_document = models.FileField(upload_to='kyc/title_deeds/', null=True, blank=True)
    face_photo = models.ImageField(upload_to='kyc/faces/', null=True, blank=True)
    
    # Verification Results
    id_verified = models.BooleanField(default=False)
    id_verification_confidence = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    kra_pin_verified = models.BooleanField(default=False)
    kra_pin_number = models.CharField(max_length=20, blank=True)  # Encrypted in production
    
    face_match_verified = models.BooleanField(default=False)
    face_match_confidence = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    title_deed_verified = models.BooleanField(default=False)
    title_deed_number = models.CharField(max_length=100, blank=True)
    land_registry_verified = models.BooleanField(default=False)
    
    # AI/ML Results
    ai_verification_result = models.CharField(max_length=20, blank=True)  # MATCH, PARTIAL, FAILED
    fraud_risk_score = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    # Review Notes
    review_notes = models.TextField(blank=True)
    reviewed_by = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviewed_kyc'
    )
    reviewed_at = models.DateTimeField(null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True)  # KYC expiry (e.g., 1 year)
    
    class Meta:
        unique_together = ['user', 'role_type']
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'role_type']),
            models.Index(fields=['status']),
        ]
    
    def __str__(self):
        return f"KYC for {self.user.username} - {self.role_type} ({self.status})"
    
    @property
    def is_verified(self):
        """Check if KYC is fully verified"""
        return self.status == 'approved' and self.verification_score >= 80
    
    @property
    def verification_badge(self):
        """Get verification badge based on level and status"""
        if not self.is_verified:
            return None
        
        badges = {
            'basic': '✓ Verified',
            'standard': '✓✓ Standard Verified',
            'advanced': '✓✓✓ Advanced Verified',
            'premium': '✓✓✓✓ Premium Verified',
        }
        return badges.get(self.verification_level, '✓ Verified')
    
    def calculate_verification_score(self):
        """Calculate verification score based on completed checks"""
        score = 0
        
        if self.id_verified:
            score += 30
        if self.kra_pin_verified:
            score += 25
        if self.face_match_verified:
            score += 25
        if self.title_deed_verified:
            score += 20
        
        # Reduce score based on fraud risk
        if self.fraud_risk_score > 50:
            score = max(0, score - (self.fraud_risk_score - 50))
        
        self.verification_score = min(100, score)
        return self.verification_score


class VerificationBadge(models.Model):
    """Verification badges displayed on user profiles"""
    
    BADGE_TYPES = [
        ('id_verified', 'ID Verified'),
        ('kra_verified', 'KRA PIN Verified'),
        ('face_verified', 'Face Match Verified'),
        ('title_deed_verified', 'Title Deed Verified'),
        ('landlord_verified', 'Verified Landlord'),
        ('agent_certified', 'Certified Agent'),
        ('premium_member', 'Premium Member'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='verification_badges')
    badge_type = models.CharField(max_length=30, choices=BADGE_TYPES)
    is_active = models.BooleanField(default=True)
    issued_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        unique_together = ['user', 'badge_type']
        ordering = ['-issued_at']
    
    def __str__(self):
        return f"{self.user.username} - {self.get_badge_type_display()}"

