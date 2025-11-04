"""
Marketing frameworks models
"""
from django.db import models
import uuid


class FrameworkCandidate(models.Model):
    """Candidate framework from ingestion"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    source = models.URLField()
    source_type = models.CharField(max_length=50)  # whitelisted_source
    
    # Framework data
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    raw_data = models.JSONField(default=dict)
    
    # Review status
    status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pending'),
            ('APPROVED', 'Approved'),
            ('REJECTED', 'Rejected'),
        ],
        default='PENDING'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    reviewed_at = models.DateTimeField(null=True, blank=True)

    class Meta:
        db_table = 'framework_candidates'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.name} (from {self.source})"


class Framework(models.Model):
    """Curated marketing framework"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    candidate = models.OneToOneField(
        FrameworkCandidate,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='framework'
    )
    
    name = models.CharField(max_length=255)
    description = models.TextField()
    
    # Framework structure
    slots = models.JSONField(default=list)  # [{name, type, required, prompt}]
    rules = models.JSONField(default=list)  # [{condition, action}]
    prompts = models.JSONField(default=dict)  # {slot_name: prompt_template}
    
    # Output schema
    output_schema = models.JSONField(default=dict)  # Pydantic schema definition
    
    # Metadata
    category = models.CharField(max_length=100, blank=True)
    tags = models.JSONField(default=list)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'frameworks'
        ordering = ['name']

    def __str__(self):
        return self.name


class FrameworkUsageLog(models.Model):
    """Log framework usage"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    framework = models.ForeignKey(Framework, on_delete=models.CASCADE, related_name='usage_logs')
    brand = models.ForeignKey('brands.Brand', on_delete=models.CASCADE, related_name='framework_usages')
    
    context = models.JSONField(default=dict)  # Usage context
    result = models.JSONField(default=dict)  # Generated result
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'framework_usage_logs'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.framework.name} used by {self.brand.name}"

