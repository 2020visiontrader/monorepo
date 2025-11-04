"""
Competitor URL configuration
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import CompetitorProfileViewSet, competitor_recrawl_view

router = DefaultRouter()
router.register(r'', CompetitorProfileViewSet, basename='competitor')

urlpatterns = [
    path('<uuid:competitor_id>/recrawl', competitor_recrawl_view, name='competitor-recrawl'),
    path('', include(router.urls)),
]

