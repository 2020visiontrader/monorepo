"""
Shopify connection tests
"""
import pytest
from django.conf import settings
from rest_framework.test import APIClient
from core.models import Organization, User
from brands.models import Brand, BrandProfile
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
    RoleAssignment.objects.create(user=user, organization=org, role='ORG_ADMIN')
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


@pytest.mark.django_db
def test_connection_status_mocked_in_st(api_client, user, brand):
    """Test connection status returns mocked true in ST"""
    api_client.force_authenticate(user=user)
    api_client.force_login(user)
    
    # Set brand_id in session-like way
    response = api_client.get(f'/api/shopify/connection?brand_id={brand.id}')
    
    # In ST, should return mocked connection
    env = getattr(settings, 'ENVIRONMENT', getattr(settings, 'ENV_NAME', 'ST'))
    if env in ['ST', 'SIT']:
        assert response.status_code == 200
        assert response.data['connected'] is True
        assert 'mock-shop.myshopify.com' in response.data.get('shop', '')


@pytest.mark.django_db
def test_disconnect_returns_204(api_client, user, brand):
    """Test disconnect returns 204"""
    api_client.force_authenticate(user=user)
    api_client.force_login(user)
    
    response = api_client.post('/api/shopify/disconnect', {
        'brand_id': str(brand.id),
    })
    
    assert response.status_code == 204

