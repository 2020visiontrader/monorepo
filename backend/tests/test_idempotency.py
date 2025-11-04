"""
Idempotency key tests
"""
import pytest
import uuid as uuid_lib
from rest_framework.test import APIClient
from django.utils import timezone
from datetime import timedelta
from core.models import Organization, User, IdempotencyKey
from brands.models import Brand, BrandProfile
from content.models import ProductDraft
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
        manifest={'theme_tokens': {'primary': '#ff0000'}, 'sections': []},
    )


@pytest.mark.django_db
def test_content_generate_idempotency(api_client, user, brand, product):
    """Test content generate returns same response with same idempotency key"""
    api_client.force_authenticate(user=user)
    api_client.force_login(user)
    
    idem_key = str(uuid_lib.uuid4())
    headers = {'Idempotency-Key': idem_key}
    
    # First request
    response1 = api_client.post(
        '/api/content/generate',
        {
            'brand_id': str(brand.id),
            'product_ids': [str(product.id)],
            'fields': ['title'],
            'variants': 3,
        },
        format='json',
        headers=headers
    )
    
    assert response1.status_code == 202
    job_id_1 = response1.data.get('job_id')
    
    # Second request with same key
    response2 = api_client.post(
        '/api/content/generate',
        {
            'brand_id': str(brand.id),
            'product_ids': [str(product.id)],
            'fields': ['title'],
            'variants': 3,
        },
        format='json',
        headers=headers
    )
    
    assert response2.status_code == 202
    assert response2.data.get('job_id') == job_id_1


@pytest.mark.django_db
def test_template_apply_idempotency(api_client, user, brand, variant):
    """Test template apply returns same response with same idempotency key"""
    from brands.models import Blueprint
    
    api_client.force_authenticate(user=user)
    api_client.force_login(user)
    
    # Create initial blueprint
    Blueprint.objects.create(
        brand=brand,
        version=1,
        json={'theme_tokens': {'primary': '#000'}},
        created_by=user,
    )
    
    idem_key = str(uuid_lib.uuid4())
    headers = {'Idempotency-Key': idem_key}
    
    # First request
    response1 = api_client.post(
        f'/api/templates/variants/{variant.id}/apply',
        headers=headers
    )
    
    assert response1.status_code == 200
    version_1 = response1.data.get('version')
    
    # Second request with same key
    response2 = api_client.post(
        f'/api/templates/variants/{variant.id}/apply',
        headers=headers
    )
    
    assert response2.status_code == 200
    assert response2.data.get('version') == version_1


@pytest.mark.django_db
def test_idempotency_key_expires(api_client, user, brand, product):
    """Test idempotency key expires after 24h"""
    api_client.force_authenticate(user=user)
    api_client.force_login(user)
    
    idem_key = uuid_lib.uuid4()
    
    # Create old idempotency key (25 hours ago)
    IdempotencyKey.objects.create(
        key=idem_key,
        route='content_generate',
        user_id=user.id,
        brand_id=brand.id,
        response_status=202,
        response_data={'job_id': 'old-job-id'},
        created_at=timezone.now() - timedelta(hours=25),
    )
    
    # Request should not use old key
    response = api_client.post(
        '/api/content/generate',
        {
            'brand_id': str(brand.id),
            'product_ids': [str(product.id)],
            'fields': ['title'],
            'variants': 3,
        },
        format='json',
        headers={'Idempotency-Key': str(idem_key)}
    )
    
    # Should create new job (not return old one)
    assert response.status_code == 202
    assert response.data.get('job_id') != 'old-job-id'

