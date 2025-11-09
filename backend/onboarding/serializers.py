"""
Onboarding serializers
"""
from rest_framework import serializers
from .models import OnboardingSession, UserConsent, OnboardingScan, OnboardingSuggestion
from .validators import (
    validate_store_settings,
    validate_product_priorities,
    validate_user_consent,
    validate_suggestion
)


class OnboardingSessionSerializer(serializers.ModelSerializer):
    """Serializer for OnboardingSession"""

    is_expired = serializers.BooleanField(read_only=True)

    class Meta:
        model = OnboardingSession
        fields = [
            'session_id', 'user', 'brand', 'status', 'raw_payload',
            'completed_steps', 'current_step', 'created_at', 'updated_at',
            'expires_at', 'completed_at', 'is_expired'
        ]
        read_only_fields = [
            'session_id', 'created_at', 'updated_at', 'completed_at', 'is_expired'
        ]


class OnboardingSessionCreateSerializer(serializers.Serializer):
    """Serializer for creating a new onboarding session"""

    user_agent = serializers.CharField(required=False, allow_blank=True)
    ip_address = serializers.IPAddressField(required=False, allow_null=True)
    brand_id = serializers.UUIDField(required=False, allow_null=True)


class OnboardingSessionUpdateSerializer(serializers.Serializer):
    """Serializer for updating session answers"""

    step = serializers.CharField(required=True)
    data = serializers.JSONField(required=True)

    def validate(self, attrs):
        # Validate based on step type
        step = attrs.get('step')
        data = attrs.get('data')

        if step == 'store_settings':
            validate_store_settings(data)
        elif step == 'product_priorities':
            validate_product_priorities(data)

        return attrs


class UserConsentSerializer(serializers.ModelSerializer):
    """Serializer for UserConsent"""

    class Meta:
        model = UserConsent
        fields = [
            'id', 'session', 'consent_given', 'consent_scope',
            'timestamp', 'ip_address', 'user_agent', 'revoked', 'revoked_at'
        ]
        read_only_fields = ['id', 'timestamp', 'revoked_at']


class UserConsentCreateSerializer(serializers.Serializer):
    """Serializer for creating user consent"""

    consent_given = serializers.BooleanField(required=True)
    consent_scope = serializers.ListField(
        child=serializers.ChoiceField(choices=[
            'catalog_scan', 'analytics', 'model_training', 'marketing'
        ]),
        required=False,
        allow_empty=True
    )
    ip_address = serializers.IPAddressField(required=True)
    user_agent = serializers.CharField(required=True)

    def validate(self, attrs):
        # If consent is given, scope must be provided
        if attrs.get('consent_given') and not attrs.get('consent_scope'):
            raise serializers.ValidationError({
                'consent_scope': 'Consent scope is required when consent is given'
            })

        # Validate against schema
        validate_user_consent({
            'consent_given': attrs['consent_given'],
            'consent_scope': attrs.get('consent_scope', []),
            'timestamp': None,  # Will be set automatically
        })

        return attrs


class OnboardingScanSerializer(serializers.ModelSerializer):
    """Serializer for OnboardingScan"""

    class Meta:
        model = OnboardingScan
        fields = [
            'scan_id', 'session', 'status', 'scan_config', 'result',
            'error_message', 'progress_percentage', 'items_scanned',
            'total_items', 'created_at', 'started_at', 'finished_at',
            'celery_task_id', 'priority', 'retry_count', 'max_retries'
        ]
        read_only_fields = [
            'scan_id', 'created_at', 'started_at', 'finished_at',
            'celery_task_id', 'result', 'error_message'
        ]


class OnboardingScanCreateSerializer(serializers.Serializer):
    """Serializer for initiating a catalog scan"""

    scan_config = serializers.JSONField(required=False, default=dict)
    priority = serializers.IntegerField(required=False, default=0)

    def validate_scan_config(self, value):
        # Validate scan configuration if provided
        if value:
            from .validators import validate_scan_config
            validate_scan_config(value)
        return value


class OnboardingSuggestionSerializer(serializers.ModelSerializer):
    """Serializer for OnboardingSuggestion"""

    class Meta:
        model = OnboardingSuggestion
        fields = [
            'id', 'scan', 'suggestion_type', 'title', 'description',
            'priority', 'impact_score', 'action_required', 'estimated_effort',
            'implemented', 'dismissed', 'created_at', 'updated_at'
        ]
        read_only_fields = ['id', 'created_at', 'updated_at']


class AdminSessionListSerializer(serializers.ModelSerializer):
    """Simplified serializer for admin session list"""

    user_email = serializers.CharField(source='user.email', read_only=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True)

    class Meta:
        model = OnboardingSession
        fields = [
            'session_id', 'user_email', 'brand_name', 'status',
            'current_step', 'created_at', 'expires_at'
        ]


class AdminSessionDetailSerializer(serializers.ModelSerializer):
    """Detailed serializer for admin session details"""

    user_email = serializers.CharField(source='user.email', read_only=True)
    brand_name = serializers.CharField(source='brand.name', read_only=True)
    consents = UserConsentSerializer(many=True, read_only=True)
    scans = OnboardingScanSerializer(many=True, read_only=True)

    class Meta:
        model = OnboardingSession
        fields = [
            'session_id', 'user_email', 'brand_name', 'status',
            'raw_payload', 'completed_steps', 'current_step',
            'created_at', 'updated_at', 'expires_at', 'completed_at',
            'user_agent', 'ip_address', 'consents', 'scans'
        ]
