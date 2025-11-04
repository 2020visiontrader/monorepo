"""
Store Templates models
"""
from django.db import models
import uuid


class Template(models.Model):
    """Store template"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    brand = models.ForeignKey('brands.Brand', on_delete=models.CASCADE, related_name='templates', null=True, blank=True)
    organization = models.ForeignKey('core.Organization', on_delete=models.CASCADE, related_name='templates', null=True, blank=True)
    
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    complexity = models.CharField(max_length=50)  # Starter, Sophisticated
    source = models.CharField(max_length=50)  # curated, generated, uploaded
    
    # Template manifest (JSON)
    manifest = models.JSONField(default=dict)  # Full template schema
    
    # Metadata
    industry_tags = models.JSONField(default=list)
    preview_image_url = models.URLField(blank=True)
    
    is_active = models.BooleanField(default=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'store_templates'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class TemplateVariant(models.Model):
    """Template variant with customizations"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template = models.ForeignKey(Template, on_delete=models.CASCADE, related_name='variants')
    brand = models.ForeignKey('brands.Brand', on_delete=models.CASCADE, related_name='template_variants')
    
    name = models.CharField(max_length=255)
    
    # Variant manifest (customized)
    manifest = models.JSONField(default=dict)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'template_variants'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.template.name} - {self.name}"

