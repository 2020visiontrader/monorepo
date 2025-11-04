"""
Shopify URL configuration
"""
from django.urls import path, include
from .views import ShopifyOAuthViewSet, connection_status_view, disconnect_view
from rest_framework.routers import DefaultRouter

router = DefaultRouter()
router.register(r'oauth', ShopifyOAuthViewSet, basename='shopify-oauth')

urlpatterns = [
    path('connection', connection_status_view, name='shopify-connection'),
    path('disconnect', disconnect_view, name='shopify-disconnect'),
    path('', include(router.urls)),
]

