"""
Frameworks URL configuration
"""
from django.urls import path, include
from rest_framework.routers import DefaultRouter
from .views import FrameworkCandidateViewSet, FrameworkViewSet

router = DefaultRouter()
router.register(r'candidates', FrameworkCandidateViewSet, basename='framework-candidate')
router.register(r'', FrameworkViewSet, basename='framework')

urlpatterns = [
    path('', include(router.urls)),
]

