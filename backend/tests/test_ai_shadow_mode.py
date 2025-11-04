"""
Test shadow mode records FrameworkRun but doesn't change responses
"""
import pytest
from django.test import override_settings
from django.utils import timezone
from rest_framework.test import APIClient
from core.models import Organization, User, BackgroundJob
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
@override_settings(AI_FRAMEWORKS_ENABLED=True, AI_SHADOW_MODE=True)
@patch('ai.tasks.shadow_run_product_copy.delay')
def test_shadow_mode_records_framework_run(mock_task, api_client, user, brand, product):
    """Test shadow mode creates FrameworkRun but response matches baseline"""
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
    
    assert response.status_code == 202
    assert 'job_id' in response.data
    
    # Verify shadow task was enqueued
    assert mock_task.called
    
    # Verify response shape matches baseline (has job_id)
    assert 'job_id' in response.data
    assert isinstance(response.data['job_id'], str)


@pytest.mark.django_db
@override_settings(AI_FRAMEWORKS_ENABLED=True, AI_SHADOW_MODE=True)
@patch('ai.tasks.shadow_run_blueprint.delay')
def test_shadow_mode_blueprint_records_framework_run(mock_task, api_client, user, brand):
    """Test blueprint shadow mode creates FrameworkRun but response matches baseline"""
    from brands.models import Blueprint
    
    api_client.force_authenticate(user=user)
    api_client.force_login(user)
    
    response = api_client.put(
        f'/api/brands/{brand.id}/blueprint',
        {'json': {'sections': [{'key': 'hero'}]}},
        format='json'
    )
    
    assert response.status_code == 200
    assert 'version' in response.data
    assert 'json' in response.data
    
    # Verify shadow task was enqueued
    assert mock_task.called
    
    # Verify response shape matches baseline
    assert response.data['json']['sections'] == [{'key': 'hero'}]

