"""
Competitor models
"""
from django.db import models
from django.conf import settings
import uuid


class CompetitorProfile(models.Model):
    """Competitor website profile"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    brand = models.ForeignKey('brands.Brand', on_delete=models.CASCADE, related_name='competitors')
    url = models.URLField()
    name = models.CharField(max_length=255, blank=True)
    is_primary = models.BooleanField(default=False)
    emulate_notes = models.TextField(blank=True)
    avoid_notes = models.TextField(blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        db_table = 'competitor_profiles'
        unique_together = [['brand', 'url']]
        ordering = ['-is_primary', 'created_at']

    def __str__(self):
        return f"{self.brand.name} - {self.url}"


class CrawlRun(models.Model):
    """Track competitor crawl runs"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    competitor = models.ForeignKey(CompetitorProfile, on_delete=models.CASCADE, related_name='crawl_runs')
    status = models.CharField(
        max_length=20,
        choices=[
            ('PENDING', 'Pending'),
            ('RUNNING', 'Running'),
            ('COMPLETED', 'Completed'),
            ('FAILED', 'Failed'),
        ],
        default='PENDING'
    )
    pages_crawled = models.IntegerField(default=0)
    error = models.TextField(blank=True)
    started_at = models.DateTimeField(null=True, blank=True)
    completed_at = models.DateTimeField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'crawl_runs'
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.competitor.url} - {self.status}"


class IASignature(models.Model):
    """Information Architecture signature from competitor"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    competitor = models.ForeignKey(CompetitorProfile, on_delete=models.CASCADE, related_name='ia_signatures')
    crawl_run = models.ForeignKey(CrawlRun, on_delete=models.CASCADE, related_name='ia_signatures', null=True)
    
    # IA data
    navigation = models.JSONField(default=list)  # [{label, url, children}]
    sections = models.JSONField(default=list)  # [{type, title, content_sample}]
    taxonomy = models.JSONField(default=dict)  # Category hierarchy
    
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'ia_signatures'
        ordering = ['-created_at']

    def __str__(self):
        return f"IA for {self.competitor.url}"


class PageNode(models.Model):
    """Individual page node from competitor crawl"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    competitor = models.ForeignKey(CompetitorProfile, on_delete=models.CASCADE, related_name='pages')
    crawl_run = models.ForeignKey(CrawlRun, on_delete=models.CASCADE, related_name='pages', null=True)

    url = models.URLField()
    title = models.CharField(max_length=255, blank=True)
    page_type = models.CharField(max_length=50, blank=True)  # homepage, category, product, etc.
    depth = models.IntegerField(default=0)
    raw_html = models.TextField(blank=True)  # Snapshot of HTML
    extracted_text = models.TextField(blank=True)
    metadata = models.JSONField(default=dict)  # H1-H3, meta tags, etc.

    parent = models.ForeignKey('self', on_delete=models.CASCADE, null=True, blank=True, related_name='children')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'page_nodes'
        unique_together = [['competitor', 'url']]
        ordering = ['depth', 'created_at']

    def __str__(self):
        return f"{self.competitor.url} - {self.url}"


class CompetitorSite(models.Model):
    """Competitor website profile for scraping"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    brand = models.ForeignKey('brands.Brand', on_delete=models.CASCADE, related_name='competitor_sites')
    url = models.URLField()
    name = models.CharField(max_length=255, blank=True)
    last_scraped_at = models.DateTimeField(null=True, blank=True)
    metadata = models.JSONField(default=dict)  # Scraping config, rate limits, etc.

    class Meta:
        db_table = 'competitor_sites'
        unique_together = [['brand', 'url']]
        ordering = ['-last_scraped_at']

    def __str__(self):
        return f"{self.brand.name} - {self.url}"


class CompetitorItem(models.Model):
    """Individual scraped item from competitor site"""
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    site = models.ForeignKey(CompetitorSite, on_delete=models.CASCADE, related_name='items')

    url = models.URLField()
    title = models.CharField(max_length=255, blank=True)
    price = models.DecimalField(max_digits=10, decimal_places=2, null=True, blank=True)
    currency = models.CharField(max_length=3, blank=True, default='USD')
    availability = models.CharField(max_length=50, blank=True)
    images = models.JSONField(default=list)  # List of image URLs
    variants = models.JSONField(default=list)  # Size, color options
    raw_html = models.TextField(blank=True, null=True)  # Raw HTML snapshot
    scraped_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        db_table = 'competitor_items'
        ordering = ['-scraped_at']
        indexes = [
            models.Index(fields=['site', 'scraped_at']),
            models.Index(fields=['price', 'currency']),
        ]

    def __str__(self):
        return f"{self.site.url} - {self.title or self.url}"
