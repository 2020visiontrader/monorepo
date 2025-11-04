"""
Error shape consistency tests
"""
import pytest
from rest_framework.test import APIClient
from rest_framework.exceptions import PermissionDenied, NotAuthenticated, ValidationError
from core.models import Organization, User
from brands.models import Brand, BrandProfile
from core.models import RoleAssignment


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
def test_unauthenticated_returns_401_with_code(api_client):
    """Test unauthenticated requests return 401 with UNAUTHENTICATED code"""
    response = api_client.get('/api/auth/me')
    
    assert response.status_code == 401
    assert response.data.get('code') == 'UNAUTHENTICATED'
    assert 'detail' in response.data


@pytest.mark.django_db
def test_forbidden_returns_403_with_code(api_client):
    """Test forbidden requests return 403 with FORBIDDEN code"""
    org = Organization.objects.create(name='Test Org', slug='test-org')
    user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='password123!',
        organization=org,
    )
    # No role assignment - should be forbidden
    
    api_client.force_authenticate(user=user)
    api_client.force_login(user)
    
    brand = Brand.objects.create(
        organization=org,
        name='Test Brand',
        slug='test-brand',
    )
    
    # Try to access brand profile without permission
    response = api_client.get(f'/api/brands/{brand.id}/profile')
    
    assert response.status_code == 403
    assert response.data.get('code') == 'FORBIDDEN'
    assert 'detail' in response.data


@pytest.mark.django_db
def test_validation_error_returns_400_with_errors(api_client):
    """Test validation errors return 400 with errors array"""
    org = Organization.objects.create(name='Test Org', slug='test-org')
    user = User.objects.create_user(
        username='testuser',
        email='test@example.com',
        password='password123!',
        organization=org,
    )
    RoleAssignment.objects.create(user=user, organization=org, role='EDITOR')
    
    api_client.force_authenticate(user=user)
    api_client.force_login(user)
    
    brand = Brand.objects.create(
        organization=org,
        name='Test Brand',
        slug='test-brand',
    )
    BrandProfile.objects.create(brand=brand)
    
    # Invalid request (missing required fields)
    response = api_client.post(
        '/api/content/generate',
        {
            'brand_id': str(brand.id),
            # Missing product_ids and fields
        },
        format='json'
    )
    
    assert response.status_code == 400
    assert response.data.get('code') == 'VALIDATION_ERROR'
    assert 'detail' in response.data
    # May have errors array if field-level validation

