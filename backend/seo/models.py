"""
SEO models
"""
from django.db import models
import uuid


class SEOPlan(models.Model):
    """SEO optimization plan for a brand"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    brand = models.ForeignKey('brands.Brand', on_delete=models.CASCADE, related_name='seo_plans')
    
    # Generated SEO data
    titles = models.JSONField(default=dict)  # {product_id: title}
    meta_descriptions = models.JSONField(default=dict)
    h1_tags = models.JSONField(default=dict)
    h2_tags = models.JSONField(default=dict)
    h3_tags = models.JSONField(default=dict)
    alt_texts = models.JSONField(default=dict)
    internal_links = models.JSONField(default=dict)
    json_ld = models.JSONField(default=dict)  # Structured data
    
    # SEO analysis
    keyword_clusters = models.JSONField(default=list)
    keyword_seeds = models.JSONField(default=list)
    
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'seo_plans'
        ordering = ['-created_at']

    def __str__(self):
        return f"SEO Plan for {self.brand.name}"


class KeywordSeedSet(models.Model):
    """Keyword seed set for SEO"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    brand = models.ForeignKey('brands.Brand', on_delete=models.CASCADE, related_name='keyword_seeds')
    keywords = models.JSONField(default=list)  # List of keyword strings
    source = models.CharField(max_length=50)  # competitor, brand, manual
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'keyword_seed_sets'
        ordering = ['-created_at']

    def __str__(self):
        return f"Keywords for {self.brand.name}"

