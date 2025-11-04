"""
Brand serializers
"""
from rest_framework import serializers
from .models import Brand, BrandProfile


class BrandProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = BrandProfile
        fields = [
            'mission', 'categories', 'personas', 'tone_sliders',
            'required_terms', 'forbidden_terms', 'single_sku',
            'shopify_store', 'shopify_access_token', 'shopify_connected_at',
        ]
        read_only_fields = ['shopify_connected_at']


class BrandSerializer(serializers.ModelSerializer):
    profile = BrandProfileSerializer(read_only=True)
    
    class Meta:
        model = Brand
        fields = ['id', 'name', 'slug', 'organization', 'is_active', 'profile', 'created_at']
        read_only_fields = ['id', 'created_at']
