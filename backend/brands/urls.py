"""
Brand URL configuration
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import BrandViewSet, PathwayViewSet
from .blueprint_views import generate_blueprint
from .views_profile import brand_profile_view
from .views_blueprint import blueprint_view, blueprint_sections_view

router = DefaultRouter()
router.register(r'', BrandViewSet, basename='brand')
router.register(r'(?P<brand_id>[^/.]+)/pathways', PathwayViewSet, basename='pathway')

urlpatterns = [
    path('', include(router.urls)),
    path('<uuid:brand_id>/blueprint/generate', generate_blueprint, name='generate-blueprint'),
    path('<uuid:brand_id>/profile', brand_profile_view, name='brand-profile'),
    path('<uuid:brand_id>/blueprint', blueprint_view, name='brand-blueprint'),
    path('<uuid:brand_id>/blueprint/sections', blueprint_sections_view, name='blueprint-sections'),
]

