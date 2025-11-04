"""
Admin configuration for frameworks app
"""
from django.contrib import admin
from .models import FrameworkCandidate, Framework, FrameworkUsageLog


@admin.register(FrameworkCandidate)
class FrameworkCandidateAdmin(admin.ModelAdmin):
    list_display = ['name', 'source', 'status', 'created_at']
    list_filter = ['status', 'source_type', 'created_at']
    search_fields = ['name', 'source']


@admin.register(Framework)
class FrameworkAdmin(admin.ModelAdmin):
    list_display = ['name', 'category', 'is_active', 'created_at']
    list_filter = ['is_active', 'category', 'created_at']
    search_fields = ['name', 'description']


@admin.register(FrameworkUsageLog)
class FrameworkUsageLogAdmin(admin.ModelAdmin):
    list_display = ['framework', 'brand', 'created_at']
    list_filter = ['created_at']
    search_fields = ['framework__name', 'brand__name']

