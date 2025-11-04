"""
Tests for framework caching
"""
import pytest
from django.test import override_settings
from unittest.mock import patch, MagicMock
from ai.services.run_with_framework import run_with_framework, compute_input_hash
from ai.models import FrameworkRun
from brands.models import Brand
from core.models import Organization


@pytest.fixture
def org():
    return Organization.objects.create(name='Test Org', slug='test-org')


@pytest.fixture
def brand(org):
    from brands.models import Brand
    return Brand.objects.create(
        organization=org,
        name='Test Brand',
        slug='test-brand',
    )


@pytest.mark.django_db
@override_settings(
    AI_FRAMEWORKS_ENABLED=True,
    AI_SHADOW_MODE=True,
    AI_CACHE_TTL_DAYS=7,
)
def test_cache_hit_prevents_provider_call(brand):
    """Test that cache hit prevents provider call"""
    # Mock framework function
    framework_func = MagicMock(return_value={'output': 'test'})
    
    payload = {'test': 'data'}
    brand_id = str(brand.id)
    
    # First call - should call provider
    result1 = run_with_framework(
        framework_name='product_copy',
        brand_id=brand_id,
        payload=payload,
        framework_func=framework_func,
    )
    
    assert result1['cached'] is False
    assert framework_func.call_count == 1
    
    # Second call with same input - should use cache
    result2 = run_with_framework(
        framework_name='product_copy',
        brand_id=brand_id,
        payload=payload,
        framework_func=framework_func,
    )
    
    assert result2['cached'] is True
    assert framework_func.call_count == 1  # No additional call


@pytest.mark.django_db
@override_settings(
    AI_FRAMEWORKS_ENABLED=True,
    AI_SHADOW_MODE=True,
    AI_CACHE_TTL_DAYS=7,
)
def test_cache_hit_creates_framework_run(brand):
    """Test that cache hit creates FrameworkRun with cached=True"""
    framework_func = MagicMock(return_value={'output': 'test'})
    
    payload = {'test': 'data'}
    brand_id = str(brand.id)
    
    # First call
    run_with_framework(
        framework_name='product_copy',
        brand_id=brand_id,
        payload=payload,
        framework_func=framework_func,
    )
    
    # Second call (cache hit)
    result = run_with_framework(
        framework_name='product_copy',
        brand_id=brand_id,
        payload=payload,
        framework_func=framework_func,
    )
    
    # Check FrameworkRun was created for cache hit
    framework_run = FrameworkRun.objects.get(id=result['framework_run_id'])
    assert framework_run.cached is True
    assert framework_run.status == 'SUCCESS'
    assert framework_run.duration_ms == 0


@pytest.mark.django_db
def test_input_hash_computation():
    """Test input hash computation includes all relevant fields"""
    brand_id = 'brand-123'
    framework_name = 'product_copy'
    payload = {'product_ids': ['1', '2'], 'fields': ['title']}
    
    hash1 = compute_input_hash(brand_id, framework_name, payload, '1.0')
    hash2 = compute_input_hash(brand_id, framework_name, payload, '1.0')
    
    # Same input should produce same hash
    assert hash1 == hash2
    
    # Different policy version should produce different hash
    hash3 = compute_input_hash(brand_id, framework_name, payload, '2.0')
    assert hash1 != hash3
    
    # Different payload should produce different hash
    payload2 = {'product_ids': ['1', '3'], 'fields': ['title']}
    hash4 = compute_input_hash(brand_id, framework_name, payload2, '1.0')
    assert hash1 != hash4

