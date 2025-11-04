"""
Admin configuration for store templates app
"""
from django.contrib import admin
from .models import Template, TemplateVariant


@admin.register(Template)
class TemplateAdmin(admin.ModelAdmin):
    list_display = ['name', 'complexity', 'source', 'is_active', 'created_at']
    list_filter = ['complexity', 'source', 'is_active', 'created_at']
    search_fields = ['name', 'description']


@admin.register(TemplateVariant)
class TemplateVariantAdmin(admin.ModelAdmin):
    list_display = ['name', 'template', 'brand', 'created_at']
    list_filter = ['created_at']
    search_fields = ['name', 'template__name', 'brand__name']

