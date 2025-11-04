"""
Store Templates serializers
"""
from rest_framework import serializers
from .models import Template, TemplateVariant


class TemplateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Template
        fields = [
            'id', 'brand', 'organization', 'name', 'description',
            'complexity', 'source', 'manifest', 'industry_tags',
            'preview_image_url', 'is_active', 'created_at', 'updated_at'
        ]


class TemplateVariantSerializer(serializers.ModelSerializer):
    class Meta:
        model = TemplateVariant
        fields = [
            'id', 'template', 'brand', 'name', 'manifest',
            'created_at', 'updated_at'
        ]

