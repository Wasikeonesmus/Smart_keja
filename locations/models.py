"""
Location Intelligence System for Kenya
County → Sub-County → Ward → Estate hierarchy
"""
from django.db import models
from django.core.validators import MinValueValidator, MaxValueValidator


class County(models.Model):
    """Kenya's 47 Counties"""
    name = models.CharField(max_length=100, unique=True)
    code = models.CharField(max_length=10, unique=True, blank=True)  # County code
    region = models.CharField(max_length=50, blank=True)  # e.g., Nairobi, Coast, Rift Valley
    
    # GPS bounds
    center_latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[MinValueValidator(-4.7), MaxValueValidator(5.5)]
    )
    center_longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True,
        validators=[MinValueValidator(33.9), MaxValueValidator(41.9)]
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Counties'
        ordering = ['name']
    
    def __str__(self):
        return self.name


class SubCounty(models.Model):
    """Sub-Counties within a County"""
    county = models.ForeignKey(County, on_delete=models.CASCADE, related_name='sub_counties')
    name = models.CharField(max_length=100)
    
    # GPS bounds
    center_latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )
    center_longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Sub-Counties'
        unique_together = ['county', 'name']
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name}, {self.county.name}"


class Ward(models.Model):
    """Wards within a Sub-County"""
    sub_county = models.ForeignKey(SubCounty, on_delete=models.CASCADE, related_name='wards')
    name = models.CharField(max_length=100)
    
    # GPS bounds
    center_latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )
    center_longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Wards'
        unique_together = ['sub_county', 'name']
        ordering = ['name']
    
    def __str__(self):
        return f"{self.name}, {self.sub_county.name}"


class Estate(models.Model):
    """Estates/Areas within a Ward or Sub-County"""
    ward = models.ForeignKey(Ward, on_delete=models.SET_NULL, null=True, blank=True, related_name='estates')
    sub_county = models.ForeignKey(SubCounty, on_delete=models.CASCADE, related_name='estates')
    name = models.CharField(max_length=100)
    
    # Additional location info
    postal_code = models.CharField(max_length=10, blank=True)
    area_type = models.CharField(
        max_length=20,
        choices=[
            ('residential', 'Residential'),
            ('commercial', 'Commercial'),
            ('mixed', 'Mixed Use'),
            ('industrial', 'Industrial'),
        ],
        default='residential'
    )
    
    # GPS bounds
    center_latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )
    center_longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        null=True,
        blank=True
    )
    
    # Location metadata
    is_popular = models.BooleanField(default=False)  # Popular areas for listings
    property_count = models.IntegerField(default=0)  # Cached count of properties
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name_plural = 'Estates'
        unique_together = ['sub_county', 'name']
        ordering = ['-is_popular', 'name']
        indexes = [
            models.Index(fields=['sub_county', 'name']),
            models.Index(fields=['is_popular']),
        ]
    
    def __str__(self):
        return f"{self.name}, {self.sub_county.name}"
    
    @property
    def full_location_string(self):
        """Get full location string: Estate, Ward, Sub-County, County"""
        parts = [self.name]
        if self.ward:
            parts.append(self.ward.name)
        parts.append(self.sub_county.name)
        parts.append(self.sub_county.county.name)
        return ', '.join(parts)
    
    @property
    def county(self):
        """Get county through sub_county"""
        return self.sub_county.county


class LocationPin(models.Model):
    """GPS pins for specific locations (properties, landmarks, etc.)"""
    estate = models.ForeignKey(Estate, on_delete=models.CASCADE, related_name='pins', null=True, blank=True)
    
    # Exact GPS coordinates
    latitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        validators=[MinValueValidator(-4.7), MaxValueValidator(5.5)]
    )
    longitude = models.DecimalField(
        max_digits=9,
        decimal_places=6,
        validators=[MinValueValidator(33.9), MaxValueValidator(41.9)]
    )
    
    # Location details
    address = models.CharField(max_length=200, blank=True)
    landmark = models.CharField(max_length=200, blank=True)
    
    # Verification
    is_verified = models.BooleanField(default=False)
    verified_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        indexes = [
            models.Index(fields=['latitude', 'longitude']),
        ]
    
    def __str__(self):
        return f"Pin at ({self.latitude}, {self.longitude})"

