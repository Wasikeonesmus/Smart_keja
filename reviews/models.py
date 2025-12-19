"""
Reviews, Ratings & Trust Score System for SmartKeja
Handles tenant-landlord, host-guest, and general property reviews
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from properties.models import Property
from bookings.models import ViewingBooking, AirbnbBooking


class Review(models.Model):
    """Reviews and ratings for properties, users, and transactions"""
    
    REVIEW_TYPES = [
        ('property', 'Property Review'),
        ('landlord', 'Landlord Review'),
        ('tenant', 'Tenant Review'),
        ('host', 'Host Review'),
        ('guest', 'Guest Review'),
        ('agent', 'Agent Review'),
        ('caretaker', 'Caretaker Review'),
    ]
    
    # Review subject
    review_type = models.CharField(max_length=20, choices=REVIEW_TYPES)
    
    # Property review
    property = models.ForeignKey(
        Property,
        on_delete=models.CASCADE,
        related_name='reviews',
        null=True,
        blank=True
    )
    
    # User reviews (landlord, tenant, host, guest, agent, caretaker)
    reviewed_user = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='received_reviews',
        null=True,
        blank=True
    )
    
    # Reviewer
    reviewer = models.ForeignKey(
        User,
        on_delete=models.CASCADE,
        related_name='given_reviews'
    )
    
    # Rating (1-5 stars)
    rating = models.IntegerField(
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    
    # Review content
    title = models.CharField(max_length=200, blank=True)
    comment = models.TextField()
    
    # Specific ratings (for property reviews)
    cleanliness_rating = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    location_rating = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    value_rating = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    communication_rating = models.IntegerField(
        null=True,
        blank=True,
        validators=[MinValueValidator(1), MaxValueValidator(5)]
    )
    
    # Related booking (if applicable)
    viewing_booking = models.ForeignKey(
        ViewingBooking,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviews'
    )
    airbnb_booking = models.ForeignKey(
        AirbnbBooking,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='reviews'
    )
    
    # Moderation
    is_verified = models.BooleanField(default=False)  # Verified purchase/booking
    is_approved = models.BooleanField(default=True)  # Admin approval
    is_flagged = models.BooleanField(default=False)  # Flagged for review
    
    # Helpful votes
    helpful_count = models.IntegerField(default=0)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['property', 'rating']),
            models.Index(fields=['reviewed_user', 'review_type']),
            models.Index(fields=['reviewer', 'review_type']),
            models.Index(fields=['is_approved', 'is_verified']),
        ]
    
    def __str__(self):
        if self.property:
            return f"{self.rating}★ review for {self.property.name} by {self.reviewer.username}"
        elif self.reviewed_user:
            return f"{self.rating}★ review for {self.reviewed_user.username} by {self.reviewer.username}"
        return f"{self.rating}★ review by {self.reviewer.username}"


class ReviewHelpful(models.Model):
    """Track which reviews users found helpful"""
    review = models.ForeignKey(Review, on_delete=models.CASCADE, related_name='helpful_votes')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='helpful_votes')
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        unique_together = ['review', 'user']
    
    def __str__(self):
        return f"{self.user.username} found review helpful"


class TrustScore(models.Model):
    """AI-calculated trust score for users"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='trust_score')
    
    # Overall trust score (0-100)
    overall_score = models.IntegerField(
        default=50,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    # Component scores
    verification_score = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    review_score = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    transaction_score = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    response_score = models.IntegerField(
        default=0,
        validators=[MinValueValidator(0), MaxValueValidator(100)]
    )
    
    # Metrics
    total_reviews = models.IntegerField(default=0)
    average_rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    response_rate = models.DecimalField(max_digits=5, decimal_places=2, default=0.0)  # Percentage
    response_time_hours = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Badges
    is_verified_host = models.BooleanField(default=False)
    is_super_host = models.BooleanField(default=False)
    is_verified_landlord = models.BooleanField(default=False)
    
    # Timestamps
    last_calculated = models.DateTimeField(auto_now=True)
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-overall_score']
    
    def __str__(self):
        return f"Trust Score for {self.user.username}: {self.overall_score}/100"
    
    def calculate_score(self):
        """Calculate overall trust score from components"""
        # Weighted average
        self.overall_score = int(
            (self.verification_score * 0.3) +
            (self.review_score * 0.3) +
            (self.transaction_score * 0.2) +
            (self.response_score * 0.2)
        )
        return self.overall_score
    
    def save(self, *args, **kwargs):
        self.calculate_score()
        super().save(*args, **kwargs)
