"""
AI framework models
"""
from django.db import models
import uuid
import hashlib
import json


class BrandAIConfig(models.Model):
    """Brand-specific AI configuration"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    brand = models.OneToOneField('brands.Brand', on_delete=models.CASCADE, related_name='ai_config')
    
    # Feature flags per brand
    frameworks_enabled = models.BooleanField(default=False)
    shadow_mode = models.BooleanField(default=True)
    autopilot_enabled = models.BooleanField(default=False)
    
    # Provider settings
    provider = models.CharField(max_length=50, default='abacus')
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    class Meta:
        db_table = 'brand_ai_configs'
    
    def __str__(self):
        return f"{self.brand.name} AI Config"


class BrandMemory(models.Model):
    """Brand memory for AI context"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    brand = models.ForeignKey('brands.Brand', on_delete=models.CASCADE, related_name='ai_memories')
    
    memory_type = models.CharField(max_length=50)  # 'competitor_insight', 'user_feedback', etc.
    content = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'brand_memories'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['brand', 'memory_type']),
        ]
    
    def __str__(self):
        return f"{self.brand.name} - {self.memory_type}"


class FrameworkRun(models.Model):
    """Track AI framework runs (shadow mode or active)"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    brand_id = models.UUIDField()
    
    framework_name = models.CharField(max_length=50)  # 'product_copy', 'seo', 'blueprint'
    framework_version = models.CharField(max_length=20, default='1.0')
    
    # Input/output tracking
    input_hash = models.CharField(max_length=64, db_index=True)  # SHA256 of input JSON
    input_data = models.JSONField()
    output_data = models.JSONField(null=True, blank=True)
    
    # Baseline comparison (for shadow mode)
    baseline_output = models.JSONField(null=True, blank=True)
    diff_summary = models.JSONField(null=True, blank=True)  # {keys_changed: [], length_diff: {}, lint_results: {}}
    
    # Status
    status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pending'),
            ('RUNNING', 'Running'),
            ('SUCCESS', 'Success'),
            ('FAILED', 'Failed'),
            ('TIMEOUT', 'Timeout'),
        ],
        default='PENDING'
    )
    
    # Timing
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    
    # Error tracking
    error_message = models.TextField(blank=True)
    error_traceback = models.TextField(blank=True)
    
    # Shadow mode flag
    is_shadow = models.BooleanField(default=True)
    
    # Telemetry fields
    duration_ms = models.IntegerField(null=True, blank=True)
    model_tier = models.CharField(max_length=50, blank=True)  # 'mock', 'standard', 'premium', 'cached'
    model_name = models.CharField(max_length=100, blank=True)  # Provider model name
    used_mock = models.BooleanField(default=True)
    cached = models.BooleanField(default=False)  # True if this was a cache hit
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'framework_runs'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['brand_id', 'framework_name', 'created_at']),
            models.Index(fields=['input_hash']),
            models.Index(fields=['status', 'is_shadow']),
        ]
    
    def __str__(self):
        return f"{self.framework_name} - {self.status} - {self.brand_id}"
    
    @staticmethod
    def hash_input(input_data: dict) -> str:
        """Generate hash of input data for deduplication"""
        json_str = json.dumps(input_data, sort_keys=True)
        return hashlib.sha256(json_str.encode()).hexdigest()


class SiteSnapshot(models.Model):
    """Site snapshot for autopilot"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    brand_id = models.UUIDField()
    
    snapshot_type = models.CharField(max_length=50)  # 'full', 'content', 'seo', 'blueprint'
    snapshot_data = models.JSONField()
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'site_snapshots'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['brand_id', 'snapshot_type', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.brand_id} - {self.snapshot_type} - {self.created_at}"


class ChangeSet(models.Model):
    """Change set for autopilot"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    brand_id = models.UUIDField()
    
    change_type = models.CharField(max_length=50)  # 'content', 'seo', 'blueprint'
    changes = models.JSONField()  # {field: {before: ..., after: ...}}
    
    status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pending'),
            ('APPROVED', 'Approved'),
            ('REJECTED', 'Rejected'),
            ('APPLIED', 'Applied'),
        ],
        default='PENDING'
    )
    
    approved_by = models.ForeignKey('core.User', on_delete=models.SET_NULL, null=True, blank=True)
    approved_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    
    class Meta:
        db_table = 'change_sets'
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['brand_id', 'status', 'created_at']),
        ]
    
    def __str__(self):
        return f"{self.brand_id} - {self.change_type} - {self.status}"

