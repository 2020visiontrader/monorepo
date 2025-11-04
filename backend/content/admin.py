"""
Admin configuration for content app
"""
from django.contrib import admin
from .models import ProductDraft, ContentVariant, PublishJob, AuditLog


@admin.register(ProductDraft)
class ProductDraftAdmin(admin.ModelAdmin):
    list_display = ['original_title', 'brand', 'shopify_product_id', 'created_at']
    list_filter = ['created_at', 'brand']
    search_fields = ['original_title', 'shopify_product_id']


@admin.register(ContentVariant)
class ContentVariantAdmin(admin.ModelAdmin):
    list_display = ['product_draft', 'variant_number', 'is_accepted', 'is_rejected', 'created_at']
    list_filter = ['is_accepted', 'is_rejected', 'created_at']
    search_fields = ['product_draft__original_title']


@admin.register(PublishJob)
class PublishJobAdmin(admin.ModelAdmin):
    list_display = ['brand', 'scope', 'status', 'items_published', 'created_at']
    list_filter = ['status', 'scope', 'created_at']
    search_fields = ['brand__name']


@admin.register(AuditLog)
class AuditLogAdmin(admin.ModelAdmin):
    list_display = ['action', 'resource_type', 'brand', 'user', 'created_at']
    list_filter = ['action', 'resource_type', 'created_at']
    search_fields = ['resource_id']

