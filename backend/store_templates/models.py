"""
Store Templates models
"""
from django.db import models
import uuid


class Template(models.Model):
    """Store template with support for built-in and uploaded templates"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    brand = models.ForeignKey('brands.Brand', on_delete=models.CASCADE, related_name='templates', null=True, blank=True)
    organization = models.ForeignKey('core.Organization', on_delete=models.CASCADE, related_name='templates', null=True, blank=True)

    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    complexity = models.CharField(max_length=50)  # Starter, Sophisticated
    source = models.CharField(max_length=50)  # builtin, uploaded

    # For uploaded templates
    uploaded_by = models.ForeignKey('core.User', on_delete=models.SET_NULL, null=True, blank=True)
    supabase_raw_path = models.TextField(blank=True)  # Path to uploaded ZIP in Supabase

    # For built-in templates
    built_in_key = models.CharField(max_length=100, blank=True)  # e.g., 'minimal_tailwind'

    # Template manifest (JSON)
    manifest = models.JSONField(default=dict)  # Full template schema
    defaults = models.JSONField(default=dict)  # Default configuration values

    # Metadata
    industry_tags = models.JSONField(default=list)
    preview_image_url = models.URLField(blank=True)

    # Status
    is_active = models.BooleanField(default=True)
    last_built_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'store_templates'
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class TemplateBuild(models.Model):
    """Track template rendering builds and deployments"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    template = models.ForeignKey(Template, on_delete=models.CASCADE, related_name='builds')

    build_status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pending'),
            ('BUILDING', 'Building'),
            ('SUCCESS', 'Success'),
            ('FAILED', 'Failed'),
        ],
        default='PENDING'
    )

    built_at = models.DateTimeField(null=True, blank=True)
    build_log = models.TextField(blank=True)
    rendered_bucket_path = models.TextField(blank=True)  # Supabase path to rendered site
    build_metadata = models.JSONField(default=dict)  # Build details, context used, etc.

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'template_builds'
        ordering = ['-created_at']

    def __str__(self):
        return f"Build for {self.template.name} - {self.build_status}"


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
