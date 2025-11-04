"""
Bulk variant operations tests
"""
import pytest
from rest_framework.test import APIClient
from core.models import Organization, User
from brands.models import Brand, BrandProfile
from content.models import ProductDraft, ContentVariant
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
def variants(brand, product):
    variants = []
    for i in range(3):
        variant = ContentVariant.objects.create(
            product_draft=product,
            field_name='title',
            variant_number=i + 1,
            content='Variant ' + str(i + 1),
            is_accepted=False,
            is_rejected=False,
        )
        variants.append(variant)
    return variants


@pytest.mark.django_db
def test_bulk_accept_per_item_results(api_client, user, brand, variants):
    """Test bulk accept returns per-item results"""
    api_client.force_authenticate(user=user)
    api_client.force_login(user)
    
    variant_ids = [str(v.id) for v in variants]
    response = api_client.post(
        '/api/content/variants/bulk-accept',
        {'ids': variant_ids},
        format='json'
    )
    
    assert response.status_code == 200
    assert 'accepted' in response.data
    assert 'failed' in response.data
    assert len(response.data['accepted']) == 3
    assert len(response.data['failed']) == 0


@pytest.mark.django_db
def test_bulk_accept_rbac_enforced(api_client, org):
    """Test bulk accept enforces RBAC"""
    # Create user without access
    other_user = User.objects.create_user(
        username='otheruser',
        email='other@example.com',
        password='password123!',
        organization=org,
    )
    
    other_brand = Brand.objects.create(
        organization=org,
        name='Other Brand',
        slug='other-brand',
    )
    
    other_product = ProductDraft.objects.create(
        brand=other_brand,
        shopify_product_id='other_prod',
        original_title='Other Product',
    )
    
    other_variant = ContentVariant.objects.create(
        product_draft=other_product,
        field_name='title',
        variant_number=1,
        content='Other Variant',
    )
    
    api_client.force_authenticate(user=other_user)
    api_client.force_login(other_user)
    
    # Try to accept variant from brand user doesn't have access to
    response = api_client.post(
        '/api/content/variants/bulk-accept',
        {'ids': [str(other_variant.id)]},
        format='json'
    )
    
    # Should fail due to RBAC or return empty accepted
    assert response.status_code in [200, 403]
    if response.status_code == 200:
        assert len(response.data.get('accepted', [])) == 0


@pytest.mark.django_db
def test_bulk_reject_per_item_results(api_client, user, brand, variants):
    """Test bulk reject returns per-item results"""
    api_client.force_authenticate(user=user)
    api_client.force_login(user)
    
    variant_ids = [str(v.id) for v in variants]
    response = api_client.post(
        '/api/content/variants/bulk-reject',
        {'ids': variant_ids},
        format='json'
    )
    
    assert response.status_code == 200
    assert 'rejected' in response.data
    assert 'failed' in response.data
    assert len(response.data['rejected']) == 3

