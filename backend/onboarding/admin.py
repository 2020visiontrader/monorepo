"""
Django admin configuration for onboarding models
"""
from django.contrib import admin
from .models import OnboardingSession, UserConsent, OnboardingScan, OnboardingSuggestion


@admin.register(OnboardingSession)
class OnboardingSessionAdmin(admin.ModelAdmin):
    list_display = ['session_id', 'user', 'brand', 'status', 'current_step', 'created_at', 'expires_at']
    list_filter = ['status', 'created_at', 'expires_at']
    search_fields = ['session_id', 'user__email', 'brand__name']
    readonly_fields = ['session_id', 'created_at', 'updated_at']
    raw_id_fields = ['user', 'brand']

    fieldsets = (
        ('Session Info', {
            'fields': ('session_id', 'user', 'brand', 'status')
        }),
        ('Progress', {
            'fields': ('current_step', 'completed_steps', 'raw_payload')
        }),
        ('Lifecycle', {
            'fields': ('created_at', 'updated_at', 'expires_at', 'completed_at')
        }),
        ('Metadata', {
            'fields': ('user_agent', 'ip_address')
        }),
    )


@admin.register(UserConsent)
class UserConsentAdmin(admin.ModelAdmin):
    list_display = ['id', 'session', 'consent_given', 'timestamp', 'revoked', 'ip_address']
    list_filter = ['consent_given', 'revoked', 'timestamp']
    search_fields = ['id', 'session__session_id', 'ip_address']
    readonly_fields = ['id', 'timestamp', 'revoked_at']

    fieldsets = (
        ('Consent Details', {
            'fields': ('session', 'consent_given', 'consent_scope')
        }),
        ('Audit Trail', {
            'fields': ('timestamp', 'ip_address', 'user_agent')
        }),
        ('Revocation', {
            'fields': ('revoked', 'revoked_at', 'notes')
        }),
    )


@admin.register(OnboardingScan)
class OnboardingScanAdmin(admin.ModelAdmin):
    list_display = ['scan_id', 'session', 'status', 'progress_percentage', 'priority', 'created_at', 'finished_at']
    list_filter = ['status', 'priority', 'created_at']
    search_fields = ['scan_id', 'session__session_id', 'celery_task_id']
    readonly_fields = ['scan_id', 'created_at', 'started_at', 'finished_at']

    fieldsets = (
        ('Scan Info', {
            'fields': ('scan_id', 'session', 'status', 'priority')
        }),
        ('Configuration', {
            'fields': ('scan_config',)
        }),
        ('Progress', {
            'fields': ('progress_percentage', 'items_scanned', 'total_items')
        }),
        ('Results', {
            'fields': ('result', 'error_message')
        }),
        ('Task Info', {
            'fields': ('celery_task_id', 'retry_count', 'max_retries')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'started_at', 'finished_at')
        }),
    )


@admin.register(OnboardingSuggestion)
class OnboardingSuggestionAdmin(admin.ModelAdmin):
    list_display = ['id', 'scan', 'suggestion_type', 'title', 'priority', 'impact_score', 'implemented', 'dismissed']
    list_filter = ['suggestion_type', 'priority', 'implemented', 'dismissed', 'created_at']
    search_fields = ['id', 'title', 'description', 'scan__scan_id']
    readonly_fields = ['id', 'created_at', 'updated_at']

    fieldsets = (
        ('Suggestion Info', {
            'fields': ('scan', 'suggestion_type', 'title', 'description')
        }),
        ('Priority', {
            'fields': ('priority', 'impact_score')
        }),
        ('Action', {
            'fields': ('action_required', 'estimated_effort')
        }),
        ('Status', {
            'fields': ('implemented', 'dismissed')
        }),
        ('Timestamps', {
            'fields': ('created_at', 'updated_at')
        }),
    )
