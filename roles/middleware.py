"""
Middleware for role switching and role-based access control
"""
from django.utils.deprecation import MiddlewareMixin
from django.shortcuts import redirect
from django.urls import reverse
from .models import RoleSession, UserRole


class RoleSwitchingMiddleware(MiddlewareMixin):
    """
    Middleware that manages role switching and provides current_role to request
    """
    
    def process_request(self, request):
        """Set the current active role for the user"""
        if request.user.is_authenticated:
            try:
                # Check if tables exist by trying to query
                role_session = RoleSession.objects.get(user=request.user)
                request.current_role = role_session.current_role
            except (RoleSession.DoesNotExist, Exception):
                # Handle case where table doesn't exist yet or session doesn't exist
                try:
                    # Try to get or create primary role
                    primary_role = UserRole.objects.filter(
                        user=request.user,
                        is_active=True,
                        is_primary=True
                    ).first()
                    
                    if not primary_role:
                        # Get first active role or create tenant role
                        primary_role = UserRole.objects.filter(
                            user=request.user,
                            is_active=True
                        ).first()
                        
                        if not primary_role:
                            try:
                                primary_role = UserRole.add_role(request.user, 'tenant', is_primary=True)
                            except Exception:
                                # Tables might not exist yet
                                primary_role = None
                    
                    # Try to create role session if it doesn't exist
                    if primary_role:
                        try:
                            role_session, created = RoleSession.objects.get_or_create(
                                user=request.user,
                                defaults={'current_role': primary_role}
                            )
                            request.current_role = role_session.current_role
                        except Exception:
                            # Table doesn't exist yet
                            request.current_role = None
                    else:
                        request.current_role = None
                except Exception:
                    # Tables don't exist yet - skip role management
                    request.current_role = None
            
            # Get all user roles for context
            try:
                request.user_roles = UserRole.get_user_roles(request.user)
            except Exception:
                request.user_roles = []
        else:
            request.current_role = None
            request.user_roles = []
        
        return None

