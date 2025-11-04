"""
Blueprint tests
"""
import pytest
from rest_framework.test import APIClient
from core.models import Organization, User
from brands.models import Brand, BrandProfile, Blueprint
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
def brand(org):
    brand = Brand.objects.create(
        organization=org,
        name='Test Brand',
        slug='test-brand',
    )
    BrandProfile.objects.create(brand=brand)
    return brand


@pytest.fixture
def blueprint(brand, user):
    return Blueprint.objects.create(
        brand=brand,
        version=1,
        json={
            'sections': [
                {'key': 'hero', 'enabled': True},
                {'key': 'features', 'enabled': False},
            ]
        },
        created_by=user,
    )


@pytest.mark.django_db
def test_blueprint_sections_increments_version(api_client, user, brand, blueprint):
    """Test blueprint sections endpoint increments version"""
    api_client.force_authenticate(user=user)
    api_client.force_login(user)
    
    response = api_client.post(
        f'/api/brands/{brand.id}/blueprint/sections',
        {
            'action': 'enable',
            'section_key': 'features',
        },
        format='json'
    )
    
    assert response.status_code == 200
    assert response.data['version'] == 2
    assert 'json' in response.data
    
    # Verify section was enabled
    sections = response.data['json'].get('sections', [])
    features_section = next((s for s in sections if s.get('key') == 'features'), None)
    assert features_section is not None
    assert features_section.get('enabled') is True


@pytest.mark.django_db
def test_blueprint_sections_updates_json(api_client, user, brand, blueprint):
    """Test blueprint sections endpoint updates JSON"""
    api_client.force_authenticate(user=user)
    api_client.force_login(user)
    
    response = api_client.post(
        f'/api/brands/{brand.id}/blueprint/sections',
        {
            'action': 'add',
            'section_key': 'test_section',
            'props': {'name': 'Test Section'},
        },
        format='json'
    )
    
    assert response.status_code == 200
    sections = response.data['json'].get('sections', [])
    assert len(sections) == 3  # hero, features, test_section
    assert any(s.get('key') == 'test_section' for s in sections)

