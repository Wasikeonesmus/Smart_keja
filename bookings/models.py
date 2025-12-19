"""
Bookings System for SmartKeja
Handles property viewings (physical/virtual) and Airbnb reservations
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator
from decimal import Decimal
from properties.models import Property


class ViewingBooking(models.Model):
    """Property viewing appointments"""
    
    VIEWING_TYPES = [
        ('physical', 'Physical Viewing'),
        ('virtual', 'Virtual Viewing'),
    ]
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
        ('no_show', 'No Show'),
    ]
    
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='viewing_bookings')
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='viewing_bookings')
    
    # Viewing details
    viewing_type = models.CharField(max_length=20, choices=VIEWING_TYPES, default='physical')
    preferred_date = models.DateField()
    preferred_time = models.TimeField()
    alternative_date = models.DateField(null=True, blank=True)
    alternative_time = models.TimeField(null=True, blank=True)
    
    # Contact information
    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=20)
    whatsapp_updates = models.BooleanField(default=False)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    confirmed_date = models.DateField(null=True, blank=True)
    confirmed_time = models.TimeField(null=True, blank=True)
    
    # Notes
    special_requests = models.TextField(blank=True)
    cancellation_reason = models.TextField(blank=True)
    
    # Virtual viewing
    virtual_meeting_link = models.URLField(blank=True)
    virtual_meeting_platform = models.CharField(
        max_length=50,
        choices=[
            ('zoom', 'Zoom'),
            ('google_meet', 'Google Meet'),
            ('teams', 'Microsoft Teams'),
            ('whatsapp', 'WhatsApp Video'),
            ('other', 'Other'),
        ],
        blank=True
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['property', 'preferred_date']),
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status', 'preferred_date']),
        ]
    
    def __str__(self):
        return f"Viewing for {self.property.name} by {self.user.username} on {self.preferred_date}"


class AirbnbBooking(models.Model):
    """Airbnb-style bookings/reservations"""
    
    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('checked_in', 'Checked In'),
        ('checked_out', 'Checked Out'),
        ('cancelled', 'Cancelled'),
        ('refunded', 'Refunded'),
    ]
    
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='airbnb_bookings')
    guest = models.ForeignKey(User, on_delete=models.CASCADE, related_name='airbnb_reservations')
    host = models.ForeignKey(User, on_delete=models.CASCADE, related_name='hosted_bookings')
    
    # Booking dates
    check_in_date = models.DateField()
    check_out_date = models.DateField()
    number_of_nights = models.IntegerField(validators=[MinValueValidator(1)])
    number_of_guests = models.IntegerField(validators=[MinValueValidator(1)])
    
    # Pricing
    nightly_rate = models.DecimalField(max_digits=10, decimal_places=2)
    subtotal = models.DecimalField(max_digits=12, decimal_places=2)  # nights * rate
    cleaning_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    service_fee = models.DecimalField(max_digits=10, decimal_places=2, default=Decimal('0.00'))
    total_amount = models.DecimalField(max_digits=12, decimal_places=2)
    currency = models.CharField(max_length=3, default='KES')
    
    # Payment
    payment_status = models.CharField(
        max_length=20,
        choices=[
            ('pending', 'Pending'),
            ('partial', 'Partial'),
            ('paid', 'Paid'),
            ('refunded', 'Refunded'),
        ],
        default='pending'
    )
    amount_paid = models.DecimalField(max_digits=12, decimal_places=2, default=Decimal('0.00'))
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    
    # Guest information
    guest_name = models.CharField(max_length=200)
    guest_email = models.EmailField()
    guest_phone = models.CharField(max_length=20)
    special_requests = models.TextField(blank=True)
    
    # Check-in/out
    check_in_time = models.TimeField(null=True, blank=True)
    check_out_time = models.TimeField(null=True, blank=True)
    actual_check_in = models.DateTimeField(null=True, blank=True)
    actual_check_out = models.DateTimeField(null=True, blank=True)
    
    # Cancellation
    cancellation_reason = models.TextField(blank=True)
    cancellation_policy = models.CharField(
        max_length=20,
        choices=[
            ('flexible', 'Flexible'),
            ('moderate', 'Moderate'),
            ('strict', 'Strict'),
        ],
        default='moderate'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    confirmed_at = models.DateTimeField(null=True, blank=True)
    cancelled_at = models.DateTimeField(null=True, blank=True)
    
    class Meta:
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['property', 'check_in_date']),
            models.Index(fields=['guest', 'status']),
            models.Index(fields=['host', 'status']),
            models.Index(fields=['status', 'check_in_date']),
        ]
    
    def __str__(self):
        return f"Airbnb booking for {self.property.name} - {self.check_in_date} to {self.check_out_date}"
    
    def calculate_total(self):
        """Calculate total booking amount"""
        self.subtotal = self.nightly_rate * self.number_of_nights
        self.total_amount = self.subtotal + self.cleaning_fee + self.service_fee
        return self.total_amount
    
    def save(self, *args, **kwargs):
        if not self.total_amount or self.total_amount == 0:
            self.calculate_total()
        super().save(*args, **kwargs)


class BookingCalendar(models.Model):
    """Calendar for managing property availability and bookings"""
    property = models.OneToOneField(Property, on_delete=models.CASCADE, related_name='booking_calendar')
    
    # Availability settings
    is_available = models.BooleanField(default=True)
    advance_booking_days = models.IntegerField(default=30)  # How many days in advance can be booked
    minimum_booking_days = models.IntegerField(default=1)
    maximum_booking_days = models.IntegerField(null=True, blank=True)
    
    # Blocked dates (maintenance, etc.)
    blocked_dates = models.JSONField(default=list, blank=True)  # List of date strings
    
    # Time slots for viewings (if applicable)
    available_time_slots = models.JSONField(
        default=list,
        blank=True,
        help_text="List of available time slots, e.g., ['09:00', '10:00', '14:00', '15:00']"
    )
    
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Booking Calendars'
    
    def __str__(self):
        return f"Calendar for {self.property.name}"
    
    def is_date_available(self, date):
        """Check if a date is available for booking"""
        if not self.is_available:
            return False
        
        date_str = date.isoformat() if hasattr(date, 'isoformat') else str(date)
        if date_str in self.blocked_dates:
            return False
        
        # Check for existing bookings
        from django.utils import timezone
        if self.property.listing_type == 'airbnb':
            conflicting = AirbnbBooking.objects.filter(
                property=self.property,
                check_in_date__lte=date,
                check_out_date__gt=date,
                status__in=['confirmed', 'checked_in']
            ).exists()
        else:
            conflicting = ViewingBooking.objects.filter(
                property=self.property,
                preferred_date=date,
                status__in=['confirmed', 'completed']
            ).exists()
        
        return not conflicting
