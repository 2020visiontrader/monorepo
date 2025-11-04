"""
Core URL configuration
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OrganizationViewSet, UserViewSet, BackgroundJobViewSet
from .views_health import HealthView

router = DefaultRouter()
router.register(r'organizations', OrganizationViewSet, basename='organization')
router.register(r'users', UserViewSet, basename='user')

urlpatterns = [
    path('health', HealthView.as_view(), name='health'),
    path('', include(router.urls)),
]

