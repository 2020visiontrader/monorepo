"""
Dashboard URL configuration
"""
from django.urls import path
from .views import dashboard_stats_view, dashboard_activities_view

urlpatterns = [
    path('stats', dashboard_stats_view, name='dashboard-stats'),
    path('activities', dashboard_activities_view, name='dashboard-activities'),
]

