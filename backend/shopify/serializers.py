"""
Shopify serializers
"""
from rest_framework import serializers
from .models import ShopifyConnection


class ShopifyConnectionSerializer(serializers.ModelSerializer):
    class Meta:
        model = ShopifyConnection
        fields = [
            'id', 'brand', 'shop', 'scopes', 'connected_at', 'updated_at'
        ]
        read_only_fields = ['access_token']  # Don't expose token

