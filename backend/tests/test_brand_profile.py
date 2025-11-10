"""
Brand profile tests
"""
import pytest
from rest_framework.test import APIClient
from core.models import Organization, User
from brands.models import Brand, BrandProfile
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
    user = User.objects.create(
        username='testuser',
        email='test@example.com',
        first_name='Test',
        last_name='User',
    )
    user.organization = org
    user.set_password('password123!')
    user.save()
    RoleAssignment.objects.create(user=user, organization=org, role='BRAND_MANAGER')
    return user


@pytest.fixture
def brand_a(org):
    brand = Brand.objects.create(
        organization=org,
        name='Brand A',
        slug='brand-a',
    )
    BrandProfile.objects.create(brand=brand)
    return brand


@pytest.fixture
def brand_b(org):
    brand = Brand.objects.create(
        organization=org,
        name='Brand B',
        slug='brand-b',
    )
    BrandProfile.objects.create(brand=brand)
    return brand


@pytest.fixture
def competitor_a(brand_a):
    return CompetitorProfile.objects.create(
        brand=brand_a,
        url='https://example.com',
        name='Competitor A',
    )


@pytest.mark.django_db
def test_profile_get(api_client, user, brand_a):
    """Test GET brand profile"""
    api_client.force_authenticate(user=user)
    api_client.force_login(user)

    # Set organization context in headers
    response = api_client.get(
        f'/api/brands/{brand_a.id}/profile',
        HTTP_X_ORGANIZATION_ID=str(brand_a.organization_id)
    )

    assert response.status_code == 200
    assert 'mission' in response.data
    assert 'single_sku' in response.data


@pytest.mark.django_db
def test_profile_update_competitor_url_uniqueness(api_client, user, brand_a, brand_b, competitor_a):
    """Test profile update enforces competitor URL uniqueness"""
    api_client.force_authenticate(user=user)
    api_client.force_login(user)

    # Try to add same URL to brand_b
    response = api_client.put(
        f'/api/brands/{brand_b.id}/profile',
        {'competitor_urls': ['https://example.com']},
        format='json',
        HTTP_X_ORGANIZATION_ID=str(brand_b.organization_id)
    )

    assert response.status_code == 400
    assert 'already exists' in response.data['detail'].lower()


@pytest.mark.django_db
def test_profile_update_single_sku_persists(api_client, user, brand_a):
    """Test profile update persists single_sku"""
    api_client.force_authenticate(user=user)
    api_client.force_login(user)

    response = api_client.put(
        f'/api/brands/{brand_a.id}/profile',
        {'single_sku': True},
        format='json',
        HTTP_X_ORGANIZATION_ID=str(brand_a.organization_id)
    )

    assert response.status_code == 200
    assert response.data['single_sku'] is True

    # Verify persisted
    profile = BrandProfile.objects.get(brand=brand_a)
    assert profile.single_sku is True
