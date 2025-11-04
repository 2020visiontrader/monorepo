"""
Brand models
"""
from django.db import models
from django.conf import settings
import uuid


class Brand(models.Model):
    """Brand entity"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    organization = models.ForeignKey(
        'core.Organization',
        on_delete=models.CASCADE,
        related_name='brands'
    )
    name = models.CharField(max_length=255)
    slug = models.SlugField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'brands'
        unique_together = [['organization', 'slug']]
        ordering = ['-created_at']

    def __str__(self):
        return self.name


class BrandProfile(models.Model):
    """Brand profile with onboarding data"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    brand = models.OneToOneField(Brand, on_delete=models.CASCADE, related_name='profile')
    
    # Basics
    mission = models.TextField(blank=True)
    categories = models.JSONField(default=list)  # List of category strings
    personas = models.JSONField(default=list)  # List of persona objects
    
    # Tone & Lexicon
    tone_sliders = models.JSONField(default=dict)  # {professional: 0.8, friendly: 0.6, ...}
    required_terms = models.JSONField(default=list)  # List of required terms
    forbidden_terms = models.JSONField(default=list)  # List of forbidden terms
    
    # Product info
    single_sku = models.BooleanField(default=False)  # If true, cap competitor pages to 5
    
    # Shopify connection
    shopify_store = models.CharField(max_length=255, blank=True)
    shopify_access_token = models.TextField(blank=True)
    shopify_connected_at = models.DateTimeField(null=True, blank=True)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'brand_profiles'

    def __str__(self):
        return f"{self.brand.name} Profile"


class Pathway(models.Model):
    """Saved playbook/pathway for a brand"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='pathways')
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    
    # Pathway settings
    default_frameworks = models.JSONField(default=list)  # Framework IDs to use
    testing_mode = models.BooleanField(default=False)  # If true, don't actually publish
    publish_policy = models.CharField(
        max_length=20,
        choices=[
            ('AUTO', 'Auto-publish'),
            ('REVIEW', 'Require review'),
            ('MANUAL', 'Manual only'),
        ],
        default='REVIEW'
    )
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    is_active = models.BooleanField(default=True)

    class Meta:
        db_table = 'pathways'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.brand.name} - {self.name}"


class Blueprint(models.Model):
    """Site blueprint for a brand"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    brand = models.ForeignKey(Brand, on_delete=models.CASCADE, related_name='blueprints')
    version = models.IntegerField(default=1)
    json = models.JSONField(default=dict)  # Blueprint manifest
    created_at = models.DateTimeField(auto_now_add=True)
    created_by = models.ForeignKey('core.User', on_delete=models.SET_NULL, null=True, blank=True)

    class Meta:
        db_table = 'blueprints'
        ordering = ['-version']
        unique_together = [['brand', 'version']]

    def __str__(self):
        return f"{self.brand.name} - v{self.version}"
