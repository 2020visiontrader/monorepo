"""
Core models for multitenancy and RBAC
"""
from django.db import models
from django.contrib.auth.models import AbstractUser
import uuid


class Organization(models.Model):
    """Multi-tenant organization (agency or single brand)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    name = models.CharField(max_length=255)
    slug = models.SlugField(unique=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'organizations'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class User(AbstractUser):
    """Extended user model"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    email = models.EmailField(unique=True)
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='users',
        null=True,
        blank=True
    )

    class Meta:
        db_table = 'users'

    def __str__(self):
        return self.email


class Role(models.TextChoices):
    ORG_ADMIN = 'ORG_ADMIN', 'Organization Admin'
    BRAND_MANAGER = 'BRAND_MANAGER', 'Brand Manager'
    EDITOR = 'EDITOR', 'Editor'
    VIEWER = 'VIEWER', 'Viewer'


class RoleAssignment(models.Model):
    """Role assignment for users within organizations/brands"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='role_assignments')
    organization = models.ForeignKey(
        Organization,
        on_delete=models.CASCADE,
        related_name='role_assignments',
        null=True,
        blank=True
    )
    brand_id = models.UUIDField(null=True, blank=True)  # Foreign key to brands.Brand
    role = models.CharField(max_length=20, choices=Role.choices)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'role_assignments'
        unique_together = [['user', 'organization', 'brand_id', 'role']]

    def __str__(self):
        return f"{self.user.email} - {self.role}"


class BackgroundJob(models.Model):
    """Track Celery background jobs"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    task_id = models.CharField(max_length=255, unique=True)
    task_name = models.CharField(max_length=255)
    status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pending'),
            ('STARTED', 'Started'),
            ('RETRY', 'Retry'),
            ('SUCCESS', 'Success'),
            ('FAILURE', 'Failure'),
        ],
        default='PENDING'
    )
    organization_id = models.UUIDField(null=True, blank=True)
    brand_id = models.UUIDField(null=True, blank=True)
    result = models.JSONField(null=True, blank=True)
    error = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'background_jobs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['brand_id', 'created_at']),
            models.Index(fields=['organization_id', 'created_at']),
        ]

    def __str__(self):
        return f"{self.task_name} - {self.status}"


class JobLog(models.Model):
    """Job execution logs for paginated retrieval"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    job = models.ForeignKey(BackgroundJob, on_delete=models.CASCADE, related_name='logs')
    step = models.CharField(max_length=100)
    level = models.CharField(max_length=20, choices=[
        ('INFO', 'Info'),
        ('WARNING', 'Warning'),
        ('ERROR', 'Error'),
        ('SUCCESS', 'Success'),
    ], default='INFO')
    message = models.TextField()
    idx = models.IntegerField(default=0)  # For pagination ordering
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'job_logs'
        ordering = ['idx', 'created_at']
        indexes = [
            models.Index(fields=['job', 'idx']),
        ]

    def __str__(self):
        return f"{self.job.task_name} - {self.step} - {self.level}"


class IdempotencyKey(models.Model):
    """Store idempotency keys for mutating endpoints"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    key = models.UUIDField(unique=True, db_index=True)
    route = models.CharField(max_length=255)
    user_id = models.UUIDField(null=True, blank=True)
    brand_id = models.UUIDField(null=True, blank=True)
    response_status = models.IntegerField()
    response_data = models.JSONField()
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'idempotency_keys'
        indexes = [
            models.Index(fields=['key', 'route', 'user_id', 'brand_id']),
        ]
        # Auto-expire after 24h (handled by cleanup task)

    def __str__(self):
        return f"{self.route} - {self.key}"
