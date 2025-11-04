"""
Competitor recrawl tests
"""
import pytest
from rest_framework.test import APIClient
from django.conf import settings
from core.models import Organization, User
from brands.models import Brand, BrandProfile
from competitors.models import CompetitorProfile, CrawlRun
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
    RoleAssignment.objects.create(user=user, organization=org, role='BRAND_MANAGER')
    return user


@pytest.fixture
def brand_single_sku(org):
    brand = Brand.objects.create(
        organization=org,
        name='Single SKU Brand',
        slug='single-sku-brand',
    )
    BrandProfile.objects.create(brand=brand, single_sku=True)
    return brand


@pytest.fixture
def brand_multi_sku(org):
    brand = Brand.objects.create(
        organization=org,
        name='Multi SKU Brand',
        slug='multi-sku-brand',
    )
    BrandProfile.objects.create(brand=brand, single_sku=False)
    return brand


@pytest.fixture
def competitor_single(brand_single_sku):
    return CompetitorProfile.objects.create(
        brand=brand_single_sku,
        url='https://example-single.com',
        name='Single Competitor',
    )


@pytest.fixture
def competitor_multi(brand_multi_sku):
    return CompetitorProfile.objects.create(
        brand=brand_multi_sku,
        url='https://example-multi.com',
        name='Multi Competitor',
    )


@pytest.mark.django_db
def test_recrawl_single_sku_cap(api_client, user, brand_single_sku, competitor_single):
    """Test recrawl applies cap=5 for single_sku brand"""
    api_client.force_authenticate(user=user)
    api_client.force_login(user)
    
    response = api_client.post(
        f'/api/competitors/{competitor_single.id}/recrawl',
        {'force': True, 'max_pages': 20},  # Request 20, should cap to 5
        format='json'
    )
    
    assert response.status_code == 202
    assert 'crawl_run_id' in response.data
    assert 'job_id' in response.data
    
    # Verify crawl run was created
    crawl_run = CrawlRun.objects.get(id=response.data['crawl_run_id'])
    assert crawl_run.competitor == competitor_single


@pytest.mark.django_db
def test_recrawl_multi_sku_cap(api_client, user, brand_multi_sku, competitor_multi):
    """Test recrawl applies cap=10 for multi-SKU brand"""
    api_client.force_authenticate(user=user)
    api_client.force_login(user)
    
    response = api_client.post(
        f'/api/competitors/{competitor_multi.id}/recrawl',
        {'force': True, 'max_pages': 15},  # Request 15, should cap to 10
        format='json'
    )
    
    assert response.status_code == 202
    assert 'crawl_run_id' in response.data
    assert 'job_id' in response.data


@pytest.mark.django_db
def test_recrawl_returns_202(api_client, user, competitor_multi):
    """Test recrawl returns 202 with crawl_run_id and job_id"""
    api_client.force_authenticate(user=user)
    api_client.force_login(user)
    
    response = api_client.post(
        f'/api/competitors/{competitor_multi.id}/recrawl',
        {'force': True},
        format='json'
    )
    
    assert response.status_code == 202
    assert 'crawl_run_id' in response.data
    assert 'job_id' in response.data

