"""
Dashboard tests
"""
import pytest
from rest_framework.test import APIClient
from core.models import Organization, User, BackgroundJob
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
def sample_data(brand):
    # Create sample products
    ProductDraft.objects.create(
        brand=brand,
        shopify_product_id='prod1',
        original_title='Product 1',
    )
    ProductDraft.objects.create(
        brand=brand,
        shopify_product_id='prod2',
        original_title='Product 2',
    )
    
    # Create competitor
    CompetitorProfile.objects.create(
        brand=brand,
        url='https://example.com',
        name='Competitor',
    )
    
    # Create job
    BackgroundJob.objects.create(
        task_name='test_task',
        status='SUCCESS',
        brand_id=brand.id,
        organization_id=brand.organization_id,
    )


@pytest.mark.django_db
def test_dashboard_stats_returns_counts(api_client, user, brand, sample_data):
    """Test dashboard stats returns counts"""
    api_client.force_authenticate(user=user)
    api_client.force_login(user)
    
    response = api_client.get(f'/api/dashboard/stats?brand_id={brand.id}')
    
    assert response.status_code == 200
    assert 'counts' in response.data
    assert response.data['counts']['products'] == 2
    assert response.data['counts']['competitors'] == 1
    assert 'jobs' in response.data


@pytest.mark.django_db
def test_dashboard_stats_fast(api_client, user, brand, sample_data):
    """Test dashboard stats is fast (<600ms)"""
    import time
    api_client.force_authenticate(user=user)
    api_client.force_login(user)
    
    start = time.time()
    response = api_client.get(f'/api/dashboard/stats?brand_id={brand.id}')
    elapsed = time.time() - start
    
    assert response.status_code == 200
    assert elapsed < 0.6  # < 600ms


@pytest.mark.django_db
def test_dashboard_activities_returns_recent_jobs(api_client, user, brand, sample_data):
    """Test dashboard activities returns recent jobs"""
    api_client.force_authenticate(user=user)
    api_client.force_login(user)
    
    response = api_client.get(f'/api/dashboard/activities?brand_id={brand.id}')
    
    assert response.status_code == 200
    assert 'activities' in response.data
    assert len(response.data['activities']) > 0
    assert response.data['activities'][0]['type'] == 'job'

