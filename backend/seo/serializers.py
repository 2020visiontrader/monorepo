"""
SEO serializers
"""
from rest_framework import serializers
from .models import SEOPlan, KeywordSeedSet


class SEOPlanSerializer(serializers.ModelSerializer):
    class Meta:
        model = SEOPlan
        fields = [
            'id', 'brand', 'titles', 'meta_descriptions',
            'h1_tags', 'h2_tags', 'h3_tags', 'alt_texts',
            'internal_links', 'json_ld', 'keyword_clusters',
            'keyword_seeds', 'created_at', 'updated_at'
        ]


class KeywordSeedSetSerializer(serializers.ModelSerializer):
    class Meta:
        model = KeywordSeedSet
        fields = ['id', 'brand', 'keywords', 'source', 'created_at']

