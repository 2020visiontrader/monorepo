"""
Job status URL configuration
"""
from django.urls import path
from .views import BackgroundJobViewSet
from .views_jobs import job_logs_view

urlpatterns = [
    path('<uuid:pk>/status', BackgroundJobViewSet.as_view({'get': 'retrieve'}), name='job-status'),
    path('<uuid:job_id>/logs', job_logs_view, name='job-logs'),
    path('', BackgroundJobViewSet.as_view({'get': 'list'}), name='job-list'),
]

