"""
Throttling tests
"""
import pytest
from rest_framework.test import APIClient
from django.core.cache import cache
from core.models import Organization, User
from brands.models import Brand, BrandProfile
from content.models import ProductDraft
from competitors.models import CompetitorProfile
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


@pytest.fixture
def competitor(brand):
    return CompetitorProfile.objects.create(
        brand=brand,
        url='https://example.com',
        name='Competitor',
    )


@pytest.fixture(autouse=True)
def clear_cache():
    """Clear cache before each test"""
    cache.clear()
    yield
    cache.clear()


@pytest.mark.django_db
def test_content_generate_throttle(api_client, user, brand, product):
    """Test content generate is throttled at 10/min"""
    api_client.force_authenticate(user=user)
    api_client.force_login(user)
    
    # Make 11 requests rapidly
    responses = []
    for i in range(11):
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
        responses.append(response)
    
    # Last request should be throttled
    assert responses[-1].status_code == 429
    assert responses[-1].data.get('code') == 'RATE_LIMITED'
    assert 'detail' in responses[-1].data


@pytest.mark.django_db
def test_competitor_recrawl_throttle(api_client, user, competitor):
    """Test competitor recrawl is throttled at 3/min"""
    api_client.force_authenticate(user=user)
    api_client.force_login(user)
    
    # Make 4 requests rapidly
    responses = []
    for i in range(4):
        response = api_client.post(
            f'/api/competitors/{competitor.id}/recrawl',
            {'force': True},
            format='json'
        )
        responses.append(response)
    
    # Last request should be throttled
    assert responses[-1].status_code == 429
    assert responses[-1].data.get('code') == 'RATE_LIMITED'

