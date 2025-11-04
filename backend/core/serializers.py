"""
Core serializers
"""
from rest_framework import serializers
from .models import User, RoleAssignment, Organization


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ['id', 'email', 'username', 'is_active', 'is_staff']
        read_only_fields = ['id']


class RoleAssignmentSerializer(serializers.ModelSerializer):
    class Meta:
        model = RoleAssignment
        fields = ['id', 'organization', 'brand_id', 'role', 'created_at']
        read_only_fields = ['id', 'created_at']


class OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = ['id', 'name', 'slug', 'is_active']
        read_only_fields = ['id']
