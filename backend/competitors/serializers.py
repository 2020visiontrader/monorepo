"""
Competitor serializers
"""
from rest_framework import serializers
from .models import CompetitorProfile, CrawlRun, IASignature, PageNode


class CompetitorProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompetitorProfile
        fields = [
            'id', 'brand', 'url', 'name', 'is_primary',
            'emulate_notes', 'avoid_notes', 'created_at', 'updated_at'
        ]


class IASignatureSerializer(serializers.ModelSerializer):
    class Meta:
        model = IASignature
        fields = [
            'id', 'competitor', 'crawl_run', 'navigation', 'sections', 'taxonomy', 'created_at'
        ]


class PageNodeSerializer(serializers.ModelSerializer):
    class Meta:
        model = PageNode
        fields = [
            'id', 'competitor', 'crawl_run', 'url', 'title', 'page_type',
            'depth', 'extracted_text', 'metadata', 'created_at'
        ]

