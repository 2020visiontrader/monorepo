"""
Admin configuration for SEO app
"""
from django.contrib import admin
from .models import SEOPlan, KeywordSeedSet


@admin.register(SEOPlan)
class SEOPlanAdmin(admin.ModelAdmin):
    list_display = ['brand', 'created_at', 'updated_at']
    search_fields = ['brand__name']


@admin.register(KeywordSeedSet)
class KeywordSeedSetAdmin(admin.ModelAdmin):
    list_display = ['brand', 'source', 'created_at']
    list_filter = ['source', 'created_at']
    search_fields = ['brand__name']

