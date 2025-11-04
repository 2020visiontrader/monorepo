"""
Admin configuration for brands app
"""
from django.contrib import admin
from .models import Brand, BrandProfile, Pathway, Blueprint


@admin.register(Brand)
class BrandAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'organization', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at', 'organization']
    search_fields = ['name', 'slug']


@admin.register(BrandProfile)
class BrandProfileAdmin(admin.ModelAdmin):
    list_display = ['brand', 'single_sku', 'shopify_store', 'shopify_connected_at']
    list_filter = ['single_sku', 'shopify_connected_at']
    search_fields = ['brand__name']


@admin.register(Pathway)
class PathwayAdmin(admin.ModelAdmin):
    list_display = ['name', 'brand', 'publish_policy', 'testing_mode', 'is_active']
    list_filter = ['publish_policy', 'testing_mode', 'is_active', 'created_at']
    search_fields = ['name', 'brand__name']


@admin.register(Blueprint)
class BlueprintAdmin(admin.ModelAdmin):
    list_display = ['brand', 'version', 'created_at', 'created_by']
    list_filter = ['version', 'created_at']
    search_fields = ['brand__name']

