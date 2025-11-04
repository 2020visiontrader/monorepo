"""
Framework serializers
"""
from rest_framework import serializers
from .models import FrameworkCandidate, Framework


class FrameworkCandidateSerializer(serializers.ModelSerializer):
    class Meta:
        model = FrameworkCandidate
        fields = [
            'id', 'source', 'source_type', 'name', 'description',
            'raw_data', 'status', 'created_at', 'reviewed_at'
        ]


class FrameworkSerializer(serializers.ModelSerializer):
    class Meta:
        model = Framework
        fields = [
            'id', 'candidate', 'name', 'description', 'slots', 'rules',
            'prompts', 'output_schema', 'category', 'tags',
            'is_active', 'created_at', 'updated_at'
        ]

