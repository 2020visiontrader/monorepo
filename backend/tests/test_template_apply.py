"""
Template apply tests
"""
import pytest
from rest_framework.test import APIClient
from core.models import Organization, User
from brands.models import Brand, BrandProfile, Blueprint
from store_templates.models import Template, TemplateVariant
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
def template():
    return Template.objects.create(
        name='Test Template',
        complexity='Starter',
        source='curated',
        manifest={'theme_tokens': {'primary': '#000'}, 'sections': []},
    )


@pytest.fixture
def variant(brand, template):
    return TemplateVariant.objects.create(
        template=template,
        brand=brand,
        name='Test Variant',
        manifest={
            'theme_tokens': {'primary': '#ff0000'},
            'sections': [{'key': 'hero', 'enabled': True}],
        },
    )


@pytest.mark.django_db
def test_apply_variant_returns_new_version(api_client, user, brand, variant):
    """Test apply variant returns new version and diff"""
    api_client.force_authenticate(user=user)
    api_client.force_login(user)
    
    # Create initial blueprint
    Blueprint.objects.create(
        brand=brand,
        version=1,
        json={'theme_tokens': {'primary': '#000'}, 'sections': []},
        created_by=user,
    )
    
    response = api_client.post(f'/api/templates/variants/{variant.id}/apply')
    
    assert response.status_code == 200
    assert 'blueprint_id' in response.data
    assert 'version' in response.data
    assert response.data['version'] == 2
    assert 'diff' in response.data
    assert response.data['diff']['tokens_changed'] is True


@pytest.mark.django_db
def test_apply_variant_creates_version_1_if_no_blueprint(api_client, user, brand, variant):
    """Test apply variant creates version 1 if no blueprint exists"""
    api_client.force_authenticate(user=user)
    api_client.force_login(user)
    
    response = api_client.post(f'/api/templates/variants/{variant.id}/apply')
    
    assert response.status_code == 200
    assert response.data['version'] == 1

