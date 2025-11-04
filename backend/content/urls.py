"""
Content URL configuration
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import (
    ProductDraftViewSet,
    ContentVariantViewSet,
    PublishJobViewSet,
    content_generate_view,
    variants_bulk_accept_view,
    variants_bulk_reject_view,
)

router = DefaultRouter()
router.register(r'products', ProductDraftViewSet, basename='product-draft')
router.register(r'variants', ContentVariantViewSet, basename='content-variant')
router.register(r'publish', PublishJobViewSet, basename='publish-job')

urlpatterns = [
    path('generate', content_generate_view, name='content-generate'),
    path('variants/bulk-accept', variants_bulk_accept_view, name='variants-bulk-accept'),
    path('variants/bulk-reject', variants_bulk_reject_view, name='variants-bulk-reject'),
    path('', include(router.urls)),
]

