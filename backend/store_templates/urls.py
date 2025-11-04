"""
Store Templates URL configuration
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import TemplateViewSet, TemplateVariantViewSet, apply_template_variant_view

router = DefaultRouter()
router.register(r'', TemplateViewSet, basename='template')
router.register(r'variants', TemplateVariantViewSet, basename='template-variant')

urlpatterns = [
    path('variants/<uuid:variant_id>/apply', apply_template_variant_view, name='template-variant-apply'),
    path('', include(router.urls)),
]

