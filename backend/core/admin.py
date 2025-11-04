"""
Admin configuration for core app
"""
from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from .models import Organization, User, RoleAssignment, BackgroundJob, JobLog, IdempotencyKey


@admin.register(Organization)
class OrganizationAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'is_active', 'created_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['name', 'slug']


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    list_display = ['email', 'username', 'organization', 'is_staff', 'is_active']
    list_filter = ['is_staff', 'is_active', 'organization']
    search_fields = ['email', 'username']


@admin.register(RoleAssignment)
class RoleAssignmentAdmin(admin.ModelAdmin):
    list_display = ['user', 'organization', 'brand_id', 'role', 'created_at']
    list_filter = ['role', 'created_at']
    search_fields = ['user__email']


@admin.register(BackgroundJob)
class BackgroundJobAdmin(admin.ModelAdmin):
    list_display = ['task_name', 'status', 'organization_id', 'brand_id', 'created_at']
    list_filter = ['status', 'task_name', 'created_at']
    search_fields = ['task_id', 'task_name']
    readonly_fields = ['id', 'task_id', 'created_at', 'updated_at']


@admin.register(JobLog)
class JobLogAdmin(admin.ModelAdmin):
    list_display = ['job', 'step', 'level', 'idx', 'created_at']
    list_filter = ['level', 'step', 'created_at']
    search_fields = ['job__task_name', 'message']
    readonly_fields = ['id', 'created_at']


@admin.register(IdempotencyKey)
class IdempotencyKeyAdmin(admin.ModelAdmin):
    list_display = ['key', 'route', 'user_id', 'brand_id', 'response_status', 'created_at']
    list_filter = ['route', 'response_status', 'created_at']
    search_fields = ['key', 'route']
    readonly_fields = ['id', 'created_at']

