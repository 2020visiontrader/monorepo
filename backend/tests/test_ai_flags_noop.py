"""
Test that AI flags default to no-op behavior
"""
import pytest
from django.test import override_settings
from rest_framework.test import APIClient
from core.models import Organization, User
from brands.models import Brand, BrandProfile
from content.models import ProductDraft
from core.models import RoleAssignment


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
@override_settings(AI_FRAMEWORKS_ENABLED=False)
def test_content_generate_noop_when_disabled(api_client, user, brand, product):
    """Test content generate behaves identically when AI_FRAMEWORKS_ENABLED=False"""
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
    
    # Verify no FrameworkRun was created
    from ai.models import FrameworkRun
    assert FrameworkRun.objects.count() == 0


@pytest.mark.django_db
@override_settings(AI_FRAMEWORKS_ENABLED=False, AI_SHADOW_MODE=True)
def test_blueprint_noop_when_disabled(api_client, user, brand):
    """Test blueprint behaves identically when AI_FRAMEWORKS_ENABLED=False"""
    from brands.models import Blueprint
    
    api_client.force_authenticate(user=user)
    api_client.force_login(user)
    
    response = api_client.put(
        f'/api/brands/{brand.id}/blueprint',
        {'json': {'sections': []}},
        format='json'
    )
    
    assert response.status_code == 200
    assert 'version' in response.data
    assert 'json' in response.data
    
    # Verify no FrameworkRun was created
    from ai.models import FrameworkRun
    assert FrameworkRun.objects.count() == 0

