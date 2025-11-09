"""
URL configuration for onboarding app
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import OnboardingSessionViewSet, AdminOnboardingViewSet

router = DefaultRouter()
router.register(r'sessions', OnboardingSessionViewSet, basename='onboarding-session')
router.register(r'admin/sessions', AdminOnboardingViewSet, basename='admin-onboarding')

urlpatterns = [
    path('', include(router.urls)),

    # Convenience URLs for common operations
    path('start', OnboardingSessionViewSet.as_view({'post': 'create'}), name='onboarding-start'),
]
