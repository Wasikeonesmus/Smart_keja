"""
Maintenance & Repairs System for SmartKeja
Handles issue reporting, caretaker operations, and maintenance tracking
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator
from properties.models import Property
from decimal import Decimal


class MaintenanceIssue(models.Model):
    """Maintenance and repair issues reported by tenants"""
    
    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('urgent', 'Urgent'),
    ]
    
    STATUS_CHOICES = [
        ('reported', 'Reported'),
        ('acknowledged', 'Acknowledged'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    CATEGORY_CHOICES = [
        ('plumbing', 'Plumbing'),
        ('electrical', 'Electrical'),
        ('hvac', 'HVAC / Heating'),
        ('appliances', 'Appliances'),
        ('structural', 'Structural'),
        ('pest_control', 'Pest Control'),
        ('cleaning', 'Cleaning'),
        ('security', 'Security'),
        ('other', 'Other'),
    ]
    
    # Property and reporter
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='maintenance_issues')
    reported_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='reported_issues')
    
    # Issue details
    category = models.CharField(max_length=20, choices=CATEGORY_CHOICES, default='other')
    title = models.CharField(max_length=200)
    description = models.TextField()
    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='reported')
    
    # Assignment
    assigned_to = models.ForeignKey(
        User,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='assigned_maintenance_issues',
        help_text="Caretaker or maintenance staff"
    )
    
    # Location within property
    unit_number = models.CharField(max_length=50, blank=True)
    location_description = models.CharField(max_length=200, blank=True)
    
    # Media
    photos = models.JSONField(default=list, blank=True)  # List of image URLs/paths
    videos = models.JSONField(default=list, blank=True)  # List of video URLs/paths
    
    # Cost estimation
    estimated_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    actual_cost = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        validators=[MinValueValidator(Decimal('0.00'))]
    )
    
    # Timestamps
    reported_at = models.DateTimeField(auto_now_add=True)
    acknowledged_at = models.DateTimeField(null=True, blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-reported_at']
        indexes = [
            models.Index(fields=['property', 'status']),
            models.Index(fields=['reported_by', 'status']),
            models.Index(fields=['assigned_to', 'status']),
            models.Index(fields=['priority', 'status']),
        ]
    
    def __str__(self):
        return f"{self.title} - {self.property.name} ({self.status})"


class MaintenanceUpdate(models.Model):
    """Updates/notes on maintenance issues"""
    issue = models.ForeignKey(MaintenanceIssue, on_delete=models.CASCADE, related_name='updates')
    updated_by = models.ForeignKey(User, on_delete=models.CASCADE, related_name='maintenance_updates')
    
    note = models.TextField()
    status_change = models.CharField(max_length=20, blank=True)  # Previous status → New status
    
    # Media
    photos = models.JSONField(default=list, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        ordering = ['-created_at']
    
    def __str__(self):
        return f"Update for {self.issue.title} by {self.updated_by.username}"


class MaintenanceInspection(models.Model):
    """Inspection checklist for properties"""
    
    STATUS_CHOICES = [
        ('scheduled', 'Scheduled'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('cancelled', 'Cancelled'),
    ]
    
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='inspections')
    inspector = models.ForeignKey(User, on_delete=models.CASCADE, related_name='inspections')
    
    # Inspection details
    inspection_date = models.DateField()
    inspection_type = models.CharField(
        max_length=20,
        choices=[
            ('move_in', 'Move-In Inspection'),
            ('move_out', 'Move-Out Inspection'),
            ('routine', 'Routine Inspection'),
            ('maintenance', 'Maintenance Inspection'),
            ('safety', 'Safety Inspection'),
        ],
        default='routine'
    )
    
    # Checklist (stored as JSON)
    checklist = models.JSONField(
        default=dict,
        help_text="Checklist items with status, e.g., {'walls': 'good', 'plumbing': 'needs_repair'}"
    )
    
    # Findings
    findings = models.TextField(blank=True)
    recommendations = models.TextField(blank=True)
    
    # Status
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='scheduled')
    
    # Media
    photos = models.JSONField(default=list, blank=True)
    videos = models.JSONField(default=list, blank=True)
    
    # Signatures
    inspector_signature = models.TextField(blank=True)  # Base64 encoded signature
    tenant_signature = models.TextField(blank=True)
    landlord_signature = models.TextField(blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        ordering = ['-inspection_date']
    
    def __str__(self):
        return f"{self.get_inspection_type_display()} for {self.property.name} on {self.inspection_date}"


class CaretakerAssignment(models.Model):
    """Caretaker assignments to properties"""
    property = models.ForeignKey(Property, on_delete=models.CASCADE, related_name='caretaker_assignments')
    caretaker = models.ForeignKey(User, on_delete=models.CASCADE, related_name='caretaker_assignments')
    
    # Assignment details
    start_date = models.DateField()
    end_date = models.DateField(null=True, blank=True)
    is_active = models.BooleanField(default=True)
    
    # Responsibilities
    responsibilities = models.JSONField(
        default=list,
        help_text="List of responsibilities, e.g., ['maintenance', 'security', 'cleaning']"
    )
    
    # Performance
    issues_resolved = models.IntegerField(default=0)
    average_response_time_hours = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['property', 'caretaker']
        ordering = ['-created_at']
    
    def __str__(self):
        return f"{self.caretaker.username} - {self.property.name}"


class CaretakerAttendance(models.Model):
    """Caretaker attendance logs"""
    assignment = models.ForeignKey(CaretakerAssignment, on_delete=models.CASCADE, related_name='attendance_logs')
    
    # Attendance
    date = models.DateField()
    check_in_time = models.TimeField(null=True, blank=True)
    check_out_time = models.TimeField(null=True, blank=True)
    
    # Location proof
    check_in_location = models.CharField(max_length=200, blank=True)  # GPS coordinates
    check_out_location = models.CharField(max_length=200, blank=True)
    check_in_photo = models.ImageField(upload_to='caretaker/attendance/', null=True, blank=True)
    check_out_photo = models.ImageField(upload_to='caretaker/attendance/', null=True, blank=True)
    
    # Tasks completed
    tasks_completed = models.JSONField(default=list, blank=True)
    
    # Notes
    notes = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['assignment', 'date']
        ordering = ['-date']
    
    def __str__(self):
        return f"Attendance for {self.assignment.caretaker.username} on {self.date}"
