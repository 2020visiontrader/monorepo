"""
SEO URL configuration
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import SEOPlanViewSet

router = DefaultRouter()
router.register(r'plans', SEOPlanViewSet, basename='seo-plan')

urlpatterns = [
    path('', include(router.urls)),
]

