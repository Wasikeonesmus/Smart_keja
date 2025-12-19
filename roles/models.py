"""
Multi-role system for SmartKeja
Users can have multiple roles: Tenant, Landlord, Agent, Caretaker, Airbnb Host/Guest, Buyer/Seller, Developer, Lawyer, Admin
"""
from django.db import models
from django.contrib.auth.models import User
from django.core.validators import MinValueValidator, MaxValueValidator


class UserRole(models.Model):
    """Represents a role that a user can have"""
    
    ROLE_CHOICES = [
        ('tenant', 'Tenant'),
        ('landlord', 'Landlord'),
        ('agent', 'Agent'),
        ('caretaker', 'Caretaker'),
        ('airbnb_host', 'Airbnb Host'),
        ('airbnb_guest', 'Airbnb Guest'),
        ('property_buyer', 'Property Buyer'),
        ('property_seller', 'Property Seller'),
        ('developer', 'Developer'),
        ('lawyer', 'Lawyer / Mortgage Officer'),
        ('admin', 'Admin'),
    ]
    
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='roles')
    role_type = models.CharField(max_length=20, choices=ROLE_CHOICES)
    is_active = models.BooleanField(default=True)
    is_primary = models.BooleanField(default=False)  # Primary role for quick access
    
    # Role-specific metadata
    metadata = models.JSONField(default=dict, blank=True)  # Store role-specific data
    
    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        unique_together = ['user', 'role_type']
        ordering = ['-is_primary', '-created_at']
        indexes = [
            models.Index(fields=['user', 'role_type']),
            models.Index(fields=['user', 'is_active']),
        ]
    
    def __str__(self):
        return f"{self.user.username} - {self.get_role_type_display()}"
    
    @classmethod
    def get_user_roles(cls, user):
        """Get all active roles for a user"""
        return cls.objects.filter(user=user, is_active=True)
    
    @classmethod
    def user_has_role(cls, user, role_type):
        """Check if user has a specific role"""
        return cls.objects.filter(user=user, role_type=role_type, is_active=True).exists()
    
    @classmethod
    def add_role(cls, user, role_type, is_primary=False, metadata=None):
        """Add a role to a user"""
        role, created = cls.objects.get_or_create(
            user=user,
            role_type=role_type,
            defaults={
                'is_active': True,
                'is_primary': is_primary,
                'metadata': metadata or {}
            }
        )
        if not created:
            role.is_active = True
            role.is_primary = is_primary
            if metadata:
                role.metadata.update(metadata)
            role.save()
        return role


class RoleSession(models.Model):
    """Tracks the current active role for a user session"""
    user = models.OneToOneField(User, on_delete=models.CASCADE, related_name='active_role_session')
    current_role = models.ForeignKey(UserRole, on_delete=models.SET_NULL, null=True, blank=True)
    last_switched_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        verbose_name = 'Role Session'
        verbose_name_plural = 'Role Sessions'
    
    def __str__(self):
        return f"{self.user.username} - {self.current_role.get_role_type_display() if self.current_role else 'No Role'}"

