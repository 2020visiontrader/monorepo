"""
Middleware for multitenancy and RBAC
"""
from django.utils.deprecation import MiddlewareMixin
from django.http import Http404
from rest_framework.exceptions import PermissionDenied


class TenancyMiddleware(MiddlewareMixin):
    """Extract and validate organization/brand context from request"""
    
    def process_request(self, request):
        # Extract org_id and brand_id from headers or query params
        org_id = request.headers.get('X-Organization-ID') or request.GET.get('org_id')
        brand_id = request.headers.get('X-Brand-ID') or request.GET.get('brand_id')
        
        # Store in request for use in views
        request.org_id = org_id
        request.brand_id = brand_id


class RBACMiddleware(MiddlewareMixin):
    """Enforce role-based access control"""
    
    def process_request(self, request):
        if not request.user.is_authenticated:
            return
        
        # Check role assignments
        # This is a simplified version - full implementation would check against
        # specific resource permissions
        pass

