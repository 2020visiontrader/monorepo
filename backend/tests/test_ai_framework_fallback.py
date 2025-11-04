"""
Test framework fallback when AI enabled but framework fails
"""
import pytest
from django.test import override_settings
from rest_framework.test import APIClient
from core.models import Organization, User
from brands.models import Brand, BrandProfile
from content.models import ProductDraft
from core.models import RoleAssignment
from unittest.mock import patch


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def org():
    return Organization.objects.create(name='Test Org', slug='test-org')


@pytest.fixture
def user(org):
    user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='password123!',
        organization=org,
    )
    RoleAssignment.objects.create(user=user, organization=org, role='EDITOR')
    return user


@pytest.fixture
def brand(org):
    brand = Brand.objects.create(
        organization=org,
        name='Test Brand',
        slug='test-brand',
    )
    BrandProfile.objects.create(brand=brand)
    return brand


@pytest.fixture
def product(brand):
    return ProductDraft.objects.create(
        brand=brand,
        shopify_product_id='prod1',
        original_title='Product 1',
    )


@pytest.mark.django_db
@override_settings(AI_FRAMEWORKS_ENABLED=True, AI_SHADOW_MODE=False)
@patch('ai.frameworks.product_copy.generate_product_copy')
def test_framework_fallback_on_error(mock_framework, api_client, user, brand, product):
    """Test framework fallback to baseline when framework fails"""
    mock_framework.side_effect = Exception("Framework error")
    
    api_client.force_authenticate(user=user)
    api_client.force_login(user)
    
    response = api_client.post(
        '/api/content/generate',
        {
            'brand_id': str(brand.id),
            'product_ids': [str(product.id)],
            'fields': ['title'],
            'variants': 3,
        },
        format='json'
    )
    
    # Should still return 202 with job_id (baseline response)
    assert response.status_code == 202
    assert 'job_id' in response.data
    
    # Verify framework was attempted
    assert mock_framework.called


@pytest.mark.django_db
@override_settings(AI_FRAMEWORKS_ENABLED=True, AI_SHADOW_MODE=False)
@patch('ai.frameworks.blueprint.generate_blueprint')
def test_blueprint_framework_fallback_on_error(mock_framework, api_client, user, brand):
    """Test blueprint fallback to baseline when framework fails"""
    from brands.models import Blueprint
    
    mock_framework.side_effect = Exception("Framework error")
    
    api_client.force_authenticate(user=user)
    api_client.force_login(user)
    
    response = api_client.put(
        f'/api/brands/{brand.id}/blueprint',
        {'json': {'sections': []}},
        format='json'
    )
    
    # Should still return 200 with blueprint (baseline response)
    assert response.status_code == 200
    assert 'version' in response.data
    assert 'json' in response.data
    
    # Verify framework was attempted
    assert mock_framework.called

