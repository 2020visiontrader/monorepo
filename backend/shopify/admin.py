"""
Admin configuration for Shopify app
"""
from django.contrib import admin
from .models import ShopifyConnection


@admin.register(ShopifyConnection)
class ShopifyConnectionAdmin(admin.ModelAdmin):
    list_display = ['brand', 'shop', 'connected_at']
    search_fields = ['brand__name', 'shop']
    readonly_fields = ['access_token']  # Don't show token in admin

