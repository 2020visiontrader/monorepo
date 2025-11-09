"""
Onboarding models for AI-powered e-commerce onboarding system
"""
from django.db import models
from django.conf import settings
from django.utils import timezone
import uuid
from datetime import timedelta


class OnboardingSession(models.Model):
    """
    Standalone onboarding session model
    Supports both authenticated and anonymous users
    """
    SESSION_STATUS_CHOICES = [
        ('initiated', 'Initiated'),
        ('in_progress', 'In Progress'),
        ('completed', 'Completed'),
        ('expired', 'Expired'),
        ('abandoned', 'Abandoned'),
    ]

    session_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        null=True,
        blank=True,
        on_delete=models.SET_NULL,
        related_name='onboarding_sessions'
    )
    brand = models.ForeignKey(
        'brands.Brand',
        null=True,
        blank=True,
        on_delete=models.CASCADE,
        related_name='onboarding_sessions'
    )

    status = models.CharField(
        max_length=20,
        choices=SESSION_STATUS_CHOICES,
        default='initiated'
    )

    # Store all collected data as JSON
    raw_payload = models.JSONField(default=dict)

    # Track which steps have been completed
    completed_steps = models.JSONField(default=list)
    current_step = models.CharField(max_length=50, blank=True)

    # Session lifecycle
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    expires_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)

    # Metadata
    user_agent = models.TextField(blank=True)
    ip_address = models.GenericIPAddressField(null=True, blank=True)

    class Meta:
        db_table = 'onboarding_sessions'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['user', 'status']),
            models.Index(fields=['status', 'expires_at']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        user_str = self.user.email if self.user else 'Anonymous'
        return f"Session {self.session_id} - {user_str} - {self.status}"

    def save(self, *args, **kwargs):
        # Set default expiry if not set (24 hours from now)
        if not self.expires_at:
            self.expires_at = timezone.now() + timedelta(hours=24)
        super().save(*args, **kwargs)

    def is_expired(self):
        """Check if session has expired"""
        if self.expires_at:
            return timezone.now() > self.expires_at
        return False

    def mark_completed(self):
        """Mark session as completed"""
        self.status = 'completed'
        self.completed_at = timezone.now()
        self.save()

    def update_payload(self, data):
        """
        Merge new data into raw_payload
        """
        if not isinstance(self.raw_payload, dict):
            self.raw_payload = {}
        self.raw_payload.update(data)
        self.status = 'in_progress'
        self.save()


class UserConsent(models.Model):
    """
    GDPR-compliant consent management
    Records user consent for various data processing activities
    """
    CONSENT_SCOPE_CHOICES = [
        ('catalog_scan', 'Catalog Scan'),
        ('analytics', 'Analytics'),
        ('model_training', 'Model Training'),
        ('marketing', 'Marketing Communications'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(
        OnboardingSession,
        on_delete=models.CASCADE,
        related_name='consents'
    )

    # Consent details
    consent_given = models.BooleanField()
    consent_scope = models.JSONField(default=list)  # Array of consent types

    # Audit trail
    timestamp = models.DateTimeField(auto_now_add=True)
    ip_address = models.GenericIPAddressField()
    user_agent = models.TextField()

    # Revocation support
    revoked = models.BooleanField(default=False)
    revoked_at = models.DateTimeField(null=True, blank=True)

    # Additional metadata
    notes = models.TextField(blank=True)

    class Meta:
        db_table = 'user_consents'
        ordering = ['-timestamp']
        indexes = [
            models.Index(fields=['session', 'consent_given']),
            models.Index(fields=['timestamp']),
        ]

    def __str__(self):
        status = "Given" if self.consent_given else "Declined"
        revoked_str = " (Revoked)" if self.revoked else ""
        return f"Consent {self.id} - {status}{revoked_str}"

    def revoke_consent(self):
        """Revoke previously given consent"""
        self.revoked = True
        self.revoked_at = timezone.now()
        self.save()

    def has_scope(self, scope):
        """Check if a specific scope is included in consent"""
        return scope in self.consent_scope if isinstance(self.consent_scope, list) else False


class OnboardingScan(models.Model):
    """
    Catalog scan orchestration for onboarding
    Tracks the status of product catalog analysis
    """
    SCAN_STATUS_CHOICES = [
        ('queued', 'Queued'),
        ('running', 'Running'),
        ('completed', 'Completed'),
        ('failed', 'Failed'),
        ('cancelled', 'Cancelled'),
        ('timeout', 'Timeout'),
    ]

    scan_id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    session = models.ForeignKey(
        OnboardingSession,
        on_delete=models.CASCADE,
        related_name='scans'
    )

    status = models.CharField(
        max_length=20,
        choices=SCAN_STATUS_CHOICES,
        default='queued'
    )

    # Scan configuration
    scan_config = models.JSONField(default=dict)  # Configuration passed to scan task

    # Results
    result = models.JSONField(null=True, blank=True)
    error_message = models.TextField(blank=True)

    # Progress tracking
    progress_percentage = models.IntegerField(default=0)
    items_scanned = models.IntegerField(default=0)
    total_items = models.IntegerField(default=0)

    # Timestamps
    created_at = models.DateTimeField(auto_now_add=True)
    started_at = models.DateTimeField(null=True, blank=True)
    finished_at = models.DateTimeField(null=True, blank=True)

    # Celery task tracking
    celery_task_id = models.CharField(max_length=255, blank=True)

    # Priority support
    priority = models.IntegerField(default=0)  # Higher = more priority

    # Retry tracking
    retry_count = models.IntegerField(default=0)
    max_retries = models.IntegerField(default=3)

    class Meta:
        db_table = 'onboarding_scans'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['session', 'status']),
            models.Index(fields=['status', 'priority']),
            models.Index(fields=['celery_task_id']),
            models.Index(fields=['created_at']),
        ]

    def __str__(self):
        return f"Scan {self.scan_id} - {self.status}"

    def mark_running(self, celery_task_id=None):
        """Mark scan as running"""
        self.status = 'running'
        self.started_at = timezone.now()
        if celery_task_id:
            self.celery_task_id = celery_task_id
        self.save()

    def mark_completed(self, result_data):
        """Mark scan as completed with results"""
        self.status = 'completed'
        self.finished_at = timezone.now()
        self.result = result_data
        self.progress_percentage = 100
        self.save()

    def mark_failed(self, error_message):
        """Mark scan as failed with error message"""
        self.status = 'failed'
        self.finished_at = timezone.now()
        self.error_message = error_message
        self.save()

    def update_progress(self, percentage, items_scanned=None, total_items=None):
        """Update scan progress"""
        self.progress_percentage = min(percentage, 100)
        if items_scanned is not None:
            self.items_scanned = items_scanned
        if total_items is not None:
            self.total_items = total_items
        self.save()

    def can_retry(self):
        """Check if scan can be retried"""
        return self.retry_count < self.max_retries

    def increment_retry(self):
        """Increment retry count"""
        self.retry_count += 1
        self.save()


class OnboardingSuggestion(models.Model):
    """
    AI-generated suggestions based on scan results
    """
    SUGGESTION_TYPE_CHOICES = [
        ('pricing', 'Pricing'),
        ('inventory', 'Inventory'),
        ('seo', 'SEO'),
        ('marketing', 'Marketing'),
        ('content', 'Content'),
        ('product', 'Product'),
    ]

    PRIORITY_CHOICES = [
        ('low', 'Low'),
        ('medium', 'Medium'),
        ('high', 'High'),
        ('critical', 'Critical'),
    ]

    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    scan = models.ForeignKey(
        OnboardingScan,
        on_delete=models.CASCADE,
        related_name='suggestions'
    )

    suggestion_type = models.CharField(max_length=20, choices=SUGGESTION_TYPE_CHOICES)
    title = models.CharField(max_length=255)
    description = models.TextField()

    priority = models.CharField(max_length=20, choices=PRIORITY_CHOICES, default='medium')
    impact_score = models.IntegerField(default=50)  # 0-100

    # Action details
    action_required = models.TextField(blank=True)
    estimated_effort = models.CharField(max_length=50, blank=True)  # e.g., "5 minutes", "1 hour"

    # Tracking
    implemented = models.BooleanField(default=False)
    dismissed = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'onboarding_suggestions'
        ordering = ['-impact_score', '-created_at']
        indexes = [
            models.Index(fields=['scan', 'suggestion_type']),
            models.Index(fields=['priority', 'impact_score']),
        ]

    def __str__(self):
        return f"{self.suggestion_type}: {self.title}"
