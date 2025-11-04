"""
Content generation tests
"""
import pytest
from django.conf import settings
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
        shopify_product_id='prod_1',
        original_title='Test Product',
        original_description='Test description',
    )


@pytest.mark.django_db
def test_generate_variants_too_many(api_client, user, brand, product):
    """Test generate with variants > MAX_VARIANTS returns 400"""
    api_client.force_authenticate(user=user)
    
    max_variants = getattr(settings, 'MAX_VARIANTS', 10)
    response = api_client.post('/api/content/generate', {
        'brand_id': str(brand.id),
        'product_ids': [str(product.id)],
        'fields': ['title'],
        'variants': max_variants + 1,
    })
    
    assert response.status_code == 400


@pytest.mark.django_db
def test_generate_empty_fields(api_client, user, brand, product):
    """Test generate with empty fields returns 422"""
    api_client.force_authenticate(user=user)
    
    response = api_client.post('/api/content/generate', {
        'brand_id': str(brand.id),
        'product_ids': [str(product.id)],
        'fields': [],
        'variants': 3,
    })
    
    assert response.status_code == 422


@pytest.mark.django_db
def test_generate_wrong_brand(api_client, user, org):
    """Test generate with product from wrong brand returns 403"""
    other_brand = Brand.objects.create(
        organization=org,
        name='Other Brand',
        slug='other-brand',
    )
    other_product = ProductDraft.objects.create(
        brand=other_brand,
        shopify_product_id='prod_other',
        original_title='Other Product',
    )
    
    brand = Brand.objects.create(
        organization=org,
        name='Test Brand',
        slug='test-brand',
    )
    BrandProfile.objects.create(brand=brand)
    
    RoleAssignment.objects.create(user=user, organization=org, brand_id=brand.id, role='EDITOR')
    
    api_client.force_authenticate(user=user)
    
    response = api_client.post('/api/content/generate', {
        'brand_id': str(brand.id),
        'product_ids': [str(other_product.id)],
        'fields': ['title'],
        'variants': 3,
    })
    
    assert response.status_code == 403


@pytest.mark.django_db
def test_generate_success(api_client, user, brand, product):
    """Test generate returns job_id"""
    api_client.force_authenticate(user=user)
    
    response = api_client.post('/api/content/generate', {
        'brand_id': str(brand.id),
        'product_ids': [str(product.id)],
        'fields': ['title', 'description'],
        'variants': 3,
    })
    
    assert response.status_code == 202
    assert 'job_id' in response.data

