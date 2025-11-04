"""
Admin configuration for AI app
"""
from django.contrib import admin
from .models import BrandAIConfig, BrandMemory, FrameworkRun, SiteSnapshot, ChangeSet


@admin.register(BrandAIConfig)
class BrandAIConfigAdmin(admin.ModelAdmin):
    list_display = ['brand', 'frameworks_enabled', 'shadow_mode', 'autopilot_enabled', 'provider']
    list_filter = ['frameworks_enabled', 'shadow_mode', 'autopilot_enabled', 'provider']
    search_fields = ['brand__name']


@admin.register(BrandMemory)
class BrandMemoryAdmin(admin.ModelAdmin):
    list_display = ['brand', 'memory_type', 'created_at']
    list_filter = ['memory_type', 'created_at']
    search_fields = ['brand__name']


@admin.register(FrameworkRun)
class FrameworkRunAdmin(admin.ModelAdmin):
    list_display = ['framework_name', 'brand_id', 'status', 'is_shadow', 'created_at', 'duration_ms']
    list_filter = ['framework_name', 'status', 'is_shadow', 'created_at']
    search_fields = ['brand_id', 'input_hash']
    readonly_fields = ['id', 'created_at', 'started_at', 'completed_at']
    ordering = ['-created_at']


@admin.register(SiteSnapshot)
class SiteSnapshotAdmin(admin.ModelAdmin):
    list_display = ['brand_id', 'snapshot_type', 'created_at']
    list_filter = ['snapshot_type', 'created_at']
    search_fields = ['brand_id']


@admin.register(ChangeSet)
class ChangeSetAdmin(admin.ModelAdmin):
    list_display = ['brand_id', 'change_type', 'status', 'approved_by', 'created_at']
    list_filter = ['change_type', 'status', 'created_at']
    search_fields = ['brand_id']

