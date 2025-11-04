"""
Permission classes for RBAC
"""
from rest_framework import permissions


class IsAuthenticated(permissions.IsAuthenticated):
    """Require authentication"""
    pass


class IsOrgAdmin(permissions.BasePermission):
    """Allow access only to organization admins"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        # Check role assignment
        return request.user.role_assignments.filter(
            organization_id=request.org_id,
            role='ORG_ADMIN'
        ).exists()


class IsBrandManager(permissions.BasePermission):
    """Allow access to brand managers or org admins"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.role_assignments.filter(
            organization_id=request.org_id,
            brand_id=request.brand_id,
            role__in=['ORG_ADMIN', 'BRAND_MANAGER']
        ).exists()


class IsEditorOrAbove(permissions.BasePermission):
    """Allow access to editors, brand managers, or org admins"""
    
    def has_permission(self, request, view):
        if not request.user.is_authenticated:
            return False
        return request.user.role_assignments.filter(
            organization_id=request.org_id,
            brand_id=request.brand_id,
            role__in=['ORG_ADMIN', 'BRAND_MANAGER', 'EDITOR']
        ).exists()

