"""
URL configuration for ecommerce optimizer project.
"""
from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/', include('core.urls')),
    path('api/auth/', include('core.auth_urls')),
    path('api/brands/', include('brands.urls')),
    path('api/competitors/', include('competitors.urls')),
    path('api/content/', include('content.urls')),
    path('api/seo/', include('seo.urls')),
    path('api/frameworks/', include('frameworks.urls')),
    path('api/shopify/', include('shopify.urls')),
    path('api/jobs/', include('core.job_urls')),
    path('api/templates/', include('store_templates.urls')),
    path('api/dashboard/', include('dashboard.urls')),
]

