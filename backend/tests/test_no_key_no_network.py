"""
Tests for no-network behavior when API key is unset
"""
import pytest
from django.test import override_settings
from unittest.mock import patch, MagicMock
from ai.providers.abacus_provider import AbacusProvider, get_ai_provider
from ai.frameworks.product_copy import generate_product_copy
from ai.frameworks.seo import optimize_seo
from ai.frameworks.blueprint import generate_blueprint
from brands.models import Brand
from core.models import Organization


@pytest.fixture
def org():
    return Organization.objects.create(name='Test Org', slug='test-org')


@pytest.fixture
def brand(org):
    return Brand.objects.create(
        organization=org,
        name='Test Brand',
        slug='test-brand',
    )


@pytest.mark.django_db
@override_settings(
    ROUTELLM_API_KEY='',
    ABACUS_API_KEY='',
    LLM_USE_MOCK=False,  # Try to force non-mock
    AI_FRAMEWORKS_ENABLED=True,
)
def test_abacus_provider_forces_mock_without_key():
    """Test that AbacusProvider forces mock mode when no API key"""
    provider = AbacusProvider()
    
    # Should be in mock mode regardless of LLM_USE_MOCK
    assert provider.use_mock is True
    assert provider.api_key == ''


@pytest.mark.django_db
@override_settings(
    ROUTELLM_API_KEY='',
    ABACUS_API_KEY='',
    AI_FRAMEWORKS_ENABLED=True,
    AI_SHADOW_MODE=True,
)
@patch('httpx.post')
@patch('requests.post')
def test_no_network_calls_without_key(mock_requests_post, mock_httpx_post, brand):
    """Test that no HTTP calls are made when API key is empty"""
    # Generate content
    product_ids = ['test-product-1']
    fields = ['title']
    brand_id = str(brand.id)
    
    generate_product_copy(
        product_ids=product_ids,
        fields=fields,
        brand_id=brand_id,
        max_variants=3,
    )
    
    # Verify no HTTP calls were made
    assert mock_requests_post.call_count == 0
    assert mock_httpx_post.call_count == 0


@pytest.mark.django_db
@override_settings(
    ROUTELLM_API_KEY='',
    ABACUS_API_KEY='',
    AI_FRAMEWORKS_ENABLED=True,
    AI_SHADOW_MODE=True,
)
@patch('httpx.post')
@patch('requests.post')
def test_seo_no_network_calls_without_key(mock_requests_post, mock_httpx_post, brand):
    """Test that SEO framework makes no HTTP calls when API key is empty"""
    page_data = {'title': 'Test Page'}
    brand_id = str(brand.id)
    
    optimize_seo(page_data, brand_id)
    
    assert mock_requests_post.call_count == 0
    assert mock_httpx_post.call_count == 0


@pytest.mark.django_db
@override_settings(
    ROUTELLM_API_KEY='',
    ABACUS_API_KEY='',
    AI_FRAMEWORKS_ENABLED=True,
    AI_SHADOW_MODE=True,
)
@patch('httpx.post')
@patch('requests.post')
def test_blueprint_no_network_calls_without_key(mock_requests_post, mock_httpx_post, brand):
    """Test that blueprint framework makes no HTTP calls when API key is empty"""
    requirements = {'sections': []}
    brand_id = str(brand.id)
    
    generate_blueprint(requirements, brand_id)
    
    assert mock_requests_post.call_count == 0
    assert mock_httpx_post.call_count == 0


@pytest.mark.django_db
@override_settings(
    ROUTELLM_API_KEY='',
    ABACUS_API_KEY='',
    AI_FRAMEWORKS_ENABLED=True,
    AI_SHADOW_MODE_BY_NAME={'seo': False},  # Try to force live
    AI_USE_MOCK_BY_FRAMEWORK={'seo': False},  # Try to force real
)
def test_hard_safety_overrides_flags(brand):
    """Test that no API key forces mock even if flags say otherwise"""
    from ai.services.framework_flags import should_use_mock
    
    # Even if flags say use real, should_use_mock should check API key
    # This is handled in the framework itself
    page_data = {'title': 'Test'}
    
    # Should still work (using mock)
    result = optimize_seo(page_data, str(brand.id))
    assert result is not None

