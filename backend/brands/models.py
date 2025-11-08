"""
Brand models
"""
from django.db import models
from django.conf import settings
from django.db import transaction
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
    
    # Onboarding state
    onboarding_step = models.CharField(max_length=50, default='mission', choices=[
        ('mission', 'Mission'),
        ('categories', 'Categories'),
        ('personas', 'Personas'),
        ('tone', 'Tone'),
        ('products', 'Products'),
        ('shopify', 'Shopify Connection')
    ])
    completed_steps = models.JSONField(default=list)
    is_onboarding_complete = models.BooleanField(default=False)
    
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
    
    # Brand Identity (from onboarding)
    brand_identity = models.JSONField(default=dict)  # Consolidated onboarding responses
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    
    @property
    def next_steps(self):
        """Get next available steps based on current progress"""
        all_steps = [
            'mission',  # Tell us about your brand
            'categories',  # Select your categories
            'personas',  # Define your audience personas
            'tone',  # Set your brand voice
            'products',  # Product selection
            'shopify'  # Optional: Connect Shopify
        ]
        
        current_idx = all_steps.index(self.onboarding_step) if self.onboarding_step in all_steps else -1
        completed = set(self.completed_steps)
        
        # Return list of available next steps
        next_available = []
        
        for idx, step in enumerate(all_steps):
            # Step is available if:
            # 1. Not already completed
            # 2. Either current step or immediately follows a completed step
            if step not in completed and (
                step == self.onboarding_step or
                (idx > 0 and all_steps[idx-1] in completed)
            ):
                next_available.append({
                    'id': step,
                    'title': step.title(),
                    'is_current': step == self.onboarding_step,
                    'can_access': True
                })
            elif step not in completed:
                next_available.append({
                    'id': step,
                    'title': step.title(),
                    'is_current': False,
                    'can_access': False
                })
                
        return next_available
    
    @transaction.atomic
    def sync_onboarding_responses(self, response_data):
        """Sync profile with onboarding response data"""
        step = response_data.get('step')
        data = response_data.get('data', {})
        
        if step not in self.completed_steps:
            self.completed_steps.append(step)
        
        # Update brand_identity field
        brand_identity = self.brand_identity or {}
        brand_identity[step] = data
        self.brand_identity = brand_identity
        
        # Map each step to the appropriate profile field
        if step == 'mission':
            self.mission = data.get('mission', '')
            
        elif step == 'categories':
            self.categories = data.get('categories', [])
            
        elif step == 'personas':
            self.personas = data.get('personas', [])
            
        elif step == 'tone':
            self.tone_sliders = data.get('tone_sliders', {})
            self.required_terms = data.get('required_terms', [])
            self.forbidden_terms = data.get('forbidden_terms', [])
            
        elif step == 'products':
            self.single_sku = data.get('single_sku', False)
            
        elif step == 'shopify' and data.get('connected'):
            self.shopify_store = data.get('store', '')
            self.shopify_access_token = data.get('access_token', '')
            self.shopify_connected_at = data.get('connected_at')

        # Check if onboarding is complete
        required_steps = {'mission', 'categories', 'personas', 'tone', 'products'}
        if all(step in self.completed_steps for step in required_steps):
            self.is_onboarding_complete = True

        self.save()
        return True

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