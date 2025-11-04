"""
Admin configuration for competitors app
"""
from django.contrib import admin
from .models import CompetitorProfile, CrawlRun, IASignature, PageNode


@admin.register(CompetitorProfile)
class CompetitorProfileAdmin(admin.ModelAdmin):
    list_display = ['brand', 'url', 'name', 'is_primary', 'created_at']
    list_filter = ['is_primary', 'created_at']
    search_fields = ['url', 'name', 'brand__name']


@admin.register(CrawlRun)
class CrawlRunAdmin(admin.ModelAdmin):
    list_display = ['competitor', 'status', 'pages_crawled', 'created_at']
    list_filter = ['status', 'created_at']
    search_fields = ['competitor__url']


@admin.register(IASignature)
class IASignatureAdmin(admin.ModelAdmin):
    list_display = ['competitor', 'created_at']
    search_fields = ['competitor__url']


@admin.register(PageNode)
class PageNodeAdmin(admin.ModelAdmin):
    list_display = ['url', 'competitor', 'page_type', 'depth', 'created_at']
    list_filter = ['page_type', 'depth', 'created_at']
    search_fields = ['url', 'title']

