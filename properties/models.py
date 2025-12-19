from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator

# Import location models safely
try:
    from locations.models import Estate, LocationPin
except ImportError:
    Estate = None
    LocationPin = None


class Property(models.Model):
    """Unified Property model supporting Rentals, Airbnb, Commercial, Land, and Sales"""
    
    # Listing Type (Primary categorization)
    LISTING_TYPES = [
        ('rental', 'Rental'),
        ('airbnb', 'Airbnb'),
        ('commercial', 'Commercial'),
        ('land', 'Land'),
        ('sale', 'For Sale'),
    ]
    
    # Property Structure Types
    PROPERTY_TYPES = [
        ('apartment', 'Apartment'),
        ('house', 'House'),
        ('studio', 'Studio'),
        ('bedsitter', 'Bedsitter'),
        ('townhouse', 'Townhouse'),
        ('villa', 'Villa'),
        ('penthouse', 'Penthouse'),
        ('commercial_building', 'Commercial Building'),
        ('office_space', 'Office Space'),
        ('shop', 'Shop'),
        ('warehouse', 'Warehouse'),
        ('plot', 'Plot'),
        ('farm', 'Farm'),
    ]
    
    VERIFICATION_STATUS = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
        ('partial', 'Partial Match'),
        ('failed', 'Failed'),
    ]
    
    # Basic Information
    owner = models.ForeignKey(User, on_delete=models.CASCADE, related_name='properties')
    listing_type = models.CharField(max_length=20, choices=LISTING_TYPES, default='rental')
    name = models.CharField(max_length=200)
    description = models.TextField()
    property_type = models.CharField(max_length=30, choices=PROPERTY_TYPES, default='apartment')
    
    # Location Information (using new location system)
    estate = models.ForeignKey('locations.Estate', on_delete=models.SET_NULL, null=True, blank=True, related_name='properties')
    location_pin = models.ForeignKey('locations.LocationPin', on_delete=models.SET_NULL, null=True, blank=True, related_name='properties')
    
    # Legacy location fields (for backward compatibility)
    county = models.CharField(max_length=100, blank=True)
    sub_county = models.CharField(max_length=100, blank=True)
    estate_name = models.CharField(max_length=100, blank=True)  # Legacy estate name
    street_address = models.CharField(max_length=200, blank=True)
    landmark = models.CharField(max_length=200, blank=True)
    
    # GPS Coordinates
    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    
    # Property Details
    bedrooms = models.IntegerField(validators=[MinValueValidator(0)], default=0)
    bathrooms = models.IntegerField(validators=[MinValueValidator(0)], default=0)
    square_feet = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    square_meters = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Pricing (varies by listing type)
    price = models.DecimalField(max_digits=12, decimal_places=2)  # Rent/month or sale price
    deposit = models.DecimalField(max_digits=12, decimal_places=2, default=0)  # Security deposit
    currency = models.CharField(max_length=3, default='KES')
    
    # Airbnb specific
    nightly_rate = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    cleaning_fee = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    minimum_nights = models.IntegerField(default=1)
    maximum_guests = models.IntegerField(null=True, blank=True)
    
    # Multi-unit buildings
    is_multi_unit = models.BooleanField(default=False)
    total_units = models.IntegerField(null=True, blank=True)
    available_units = models.IntegerField(null=True, blank=True)
    
    # Verification
    verification_status = models.CharField(max_length=20, choices=VERIFICATION_STATUS, default='pending')
    verification_score = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    ai_verification_result = models.CharField(max_length=20, blank=True)  # MATCH, PARTIAL, FAILED
    verified_at = models.DateTimeField(null=True, blank=True)
    
    # Media Requirements
    min_photos_required = models.IntegerField(default=5)
    min_video_required = models.BooleanField(default=True)
    
    # Status
    available = models.BooleanField(default=True)
    available_from = models.DateField(null=True, blank=True)
    featured = models.BooleanField(default=False)  # Featured listings
    is_best_value = models.BooleanField(default=False)  # AI-tagged "Best Value"
    
    # Ratings
    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    review_count = models.IntegerField(default=0)
    trust_score = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])
    
    # Agent/Caretaker assignment
    assigned_agent = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_properties'
    )
    assigned_caretaker = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='caretaker_properties'
    )
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Properties'
        ordering = ['-created_at', '-featured']
        indexes = [
            models.Index(fields=['listing_type', 'available']),
            models.Index(fields=['verification_status']),
            models.Index(fields=['estate']),
            models.Index(fields=['latitude', 'longitude']),
        ]
    
    def __str__(self):
        return f"{self.name} ({self.get_listing_type_display()})"
    
    @property
    def is_verified(self):
        return self.verification_status == 'approved' and self.ai_verification_result == 'MATCH'
    
    @property
    def location_string(self):
        """Get location string, preferring new location system"""
        if self.estate:
            return self.estate.full_location_string
        # Fallback to legacy fields
        parts = [self.estate_name or self.estate.name if hasattr(self, 'estate') and self.estate else '']
        if self.sub_county:
            parts.append(self.sub_county)
        if self.county:
            parts.append(self.county)
        return ', '.join(filter(None, parts))
    
    @property
    def has_minimum_media(self):
        """Check if property has minimum required media"""
        photo_count = self.images.count()
        has_video = self.videos.filter(is_verification_video=True).exists()
        
        return photo_count >= self.min_photos_required and (not self.min_video_required or has_video)


class PropertyImage(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='images')
    image = models.ImageField(upload_to='properties/images/')
    is_primary = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-is_primary', 'uploaded_at']


class PropertyVideo(models.Model):
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='videos')
    video = models.FileField(upload_to='properties/videos/')
    is_verification_video = models.BooleanField(default=False)
    uploaded_at = models.DateTimeField(auto_now_add=True)
    
    # AI Verification Results
    location_match = models.CharField(max_length=20, blank=True)  # MATCH, PARTIAL, FAILED
    verification_confidence = models.IntegerField(default=0, validators=[MinValueValidator(0), MaxValueValidator(100)])


class PropertyAmenity(models.Model):
    AMENITY_CHOICES = [
        ('parking', 'Parking'),
        ('security', '24/7 Security'),
        ('water', 'Water Supply'),
        ('wifi', 'WiFi'),
        ('gym', 'Gym'),
        ('pool', 'Swimming Pool'),
        ('elevator', 'Elevator'),
        ('balcony', 'Balcony'),
        ('garden', 'Garden'),
        ('terrace', 'Terrace'),
        ('fireplace', 'Fireplace'),
        ('air_conditioning', 'Air Conditioning'),
        ('heating', 'Heating'),
        ('dishwasher', 'Dishwasher'),
        ('washing_machine', 'Washing Machine'),
        ('dryer', 'Dryer'),
        ('tv', 'TV'),
        ('cable_tv', 'Cable TV'),
        ('internet', 'Internet'),
        ('furnished', 'Furnished'),
        ('semi_furnished', 'Semi-Furnished'),
        ('unfurnished', 'Unfurnished'),
        ('pet_friendly', 'Pet Friendly'),
        ('smoking_allowed', 'Smoking Allowed'),
        ('wheelchair_accessible', 'Wheelchair Accessible'),
        ('near_transport', 'Near Public Transport'),
        ('near_schools', 'Near Schools'),
        ('near_hospitals', 'Near Hospitals'),
        ('near_shopping', 'Near Shopping'),
    ]
    
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='amenities')
    amenity_type = models.CharField(max_length=50, choices=AMENITY_CHOICES)
    
    class Meta:
        verbose_name_plural = 'Property Amenities'
        unique_together = ['property', 'amenity_type']


class LocationHierarchy(models.Model):
    """County → Sub-county → Estate hierarchy"""
    county = models.CharField(max_length=100)
    sub_county = models.CharField(max_length=100, blank=True)
    estate = models.CharField(max_length=100)

    # GPS bounds for the area
    center_latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    center_longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    class Meta:
        verbose_name_plural = 'Location Hierarchies'
        unique_together = ['county', 'sub_county', 'estate']

    def __str__(self):
        return f"{self.estate}, {self.sub_county or ''}, {self.county}".strip(', ')


class Booking(models.Model):
    """Booking model for property viewings"""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('confirmed', 'Confirmed'),
        ('cancelled', 'Cancelled'),
    ]

    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='bookings')
    # Optional link to user; in production you may want this required
    user = models.ForeignKey(User, on_delete=models.SET_NULL, null=True, blank=True, related_name='bookings')

    name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=50)

    date = models.DateField()
    time_slot = models.CharField(max_length=50)

    whatsapp_updates = models.BooleanField(default=False)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Booking for {self.property.name} on {self.date} at {self.time_slot}"


class LandlordApplication(models.Model):
    """Application details for a landlord/house owner to be verified before listing."""

    STATUS_CHOICES = [
        ('pending', 'Pending'),
        ('approved', 'Approved'),
        ('rejected', 'Rejected'),
    ]

    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='landlord_application')

    full_name = models.CharField(max_length=200)
    email = models.EmailField()
    phone = models.CharField(max_length=50)

    id_document = models.FileField(upload_to='landlords/ids/')

    county = models.CharField(max_length=100, blank=True)
    sub_county = models.CharField(max_length=100, blank=True)
    estate = models.CharField(max_length=100, blank=True)

    latitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)
    longitude = models.DecimalField(max_digits=9, decimal_places=6, null=True, blank=True)

    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    review_notes = models.TextField(blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Landlord application for {self.user.username} - {self.status}"
