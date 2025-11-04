"""
Content serializers
"""
from rest_framework import serializers
from .models import ProductDraft, ContentVariant, PublishJob


class ContentVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = ContentVariant
        fields = [
            'id', 'product_draft', 'variant_number', 'title', 'bullets',
            'long_description', 'framework', 'is_valid', 'validation_errors',
            'is_accepted', 'is_rejected', 'created_at'
        ]


class ProductDraftSerializer(serializers.ModelSerializer):
    variants = ContentVariantSerializer(many=True, read_only=True)
    
    class Meta:
        model = ProductDraft
        fields = [
            'id', 'brand', 'shopify_product_id', 'shopify_variant_id',
            'original_title', 'original_description', 'variants',
            'created_at', 'updated_at'
        ]


class PublishJobSerializer(serializers.ModelSerializer):
    class Meta:
        model = PublishJob
        fields = [
            'id', 'brand', 'scope', 'changeset_id', 'status',
            'items_published', 'items_failed', 'error',
            'created_at', 'updated_at'
        ]

