"""
Content models
"""
from django.db import models
from django.conf import settings
import uuid


class ProductDraft(models.Model):
    """Draft product content"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    brand = models.ForeignKey('brands.Brand', on_delete=models.CASCADE, related_name='product_drafts')
    shopify_product_id = models.CharField(max_length=255, blank=True)
    shopify_variant_id = models.CharField(max_length=255, blank=True)
    
    # Original product data
    original_title = models.CharField(max_length=255, blank=True)
    original_description = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'product_drafts'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.brand.name} - {self.original_title}"


class ContentVariant(models.Model):
    """Generated content variant with indexes for dashboard queries"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    product_draft = models.ForeignKey(ProductDraft, on_delete=models.CASCADE, related_name='variants')
    variant_number = models.IntegerField(default=1)  # 1-3
    
    # Generated content
    title = models.CharField(max_length=255)
    bullets = models.JSONField(default=list)  # List of bullet points
    long_description = models.TextField()
    
    # Framework used
    framework = models.ForeignKey('frameworks.Framework', on_delete=models.SET_NULL, null=True, blank=True)
    
    # Validation
    is_valid = models.BooleanField(default=True)
    validation_errors = models.JSONField(default=list)
    
    # Review status
    is_accepted = models.BooleanField(default=False)
    is_rejected = models.BooleanField(default=False)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'content_variants'
        unique_together = [['product_draft', 'variant_number']]
        ordering = ['variant_number']
        indexes = [
            models.Index(fields=['product_draft', 'is_accepted', 'is_rejected'], name='variant_status_idx'),
        ]

    def __str__(self):
        return f"Variant {self.variant_number} for {self.product_draft.original_title}"


class PublishJob(models.Model):
    """Track publishing jobs to Shopify"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    brand = models.ForeignKey('brands.Brand', on_delete=models.CASCADE, related_name='publish_jobs')
    scope = models.CharField(max_length=50)  # product, page, seo, etc.
    changeset_id = models.UUIDField(null=True, blank=True)
    
    status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pending'),
            ('RUNNING', 'Running'),
            ('COMPLETED', 'Completed'),
            ('FAILED', 'Failed'),
            ('ROLLED_BACK', 'Rolled Back'),
        ],
        default='PENDING'
    )
    
    items_published = models.IntegerField(default=0)
    items_failed = models.IntegerField(default=0)
    error = models.TextField(blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'publish_jobs'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.brand.name} - {self.scope} - {self.status}"


class AuditLog(models.Model):
    """Audit log for content changes"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    brand = models.ForeignKey('brands.Brand', on_delete=models.CASCADE, related_name='audit_logs')
    user = models.ForeignKey('core.User', on_delete=models.SET_NULL, null=True, blank=True)
    
    action = models.CharField(max_length=50)  # publish, rollback, generate, etc.
    resource_type = models.CharField(max_length=50)  # product, page, seo, etc.
    resource_id = models.CharField(max_length=255)
    
    changes = models.JSONField(default=dict)  # Before/after or diff
    metadata = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'audit_logs'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.action} - {self.resource_type} - {self.created_at}"

