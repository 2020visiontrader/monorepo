"""
Authentication tests
"""
import pytest
from django.contrib.auth import get_user_model
from rest_framework.test import APIClient
from core.models import Organization, RoleAssignment

User = get_user_model()


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
    RoleAssignment.objects.create(user=user, organization=org, role='ORG_ADMIN')
    return user


@pytest.mark.django_db
def test_login_invalid_credentials(api_client):
    """Test login with invalid credentials returns 401"""
    response = api_client.post('/api/auth/login', {
        'email': 'wrong@example.com',
        'password': 'wrong',
    })
    assert response.status_code == 401


@pytest.mark.django_db
def test_login_valid_credentials(api_client, user):
    """Test login with valid credentials returns 200"""
    response = api_client.post('/api/auth/login', {
        'email': 'test@example.com',
        'password': 'password123!',
    })
    assert response.status_code == 200
    assert 'user' in response.data
    assert 'roles' in response.data
    assert response.data['user']['email'] == 'test@example.com'


@pytest.mark.django_db
def test_me_requires_auth(api_client):
    """Test /api/auth/me requires authentication"""
    response = api_client.get('/api/auth/me')
    assert response.status_code == 403


@pytest.mark.django_db
def test_me_returns_user_info(api_client, user):
    """Test /api/auth/me returns user info"""
    api_client.force_authenticate(user=user)
    response = api_client.get('/api/auth/me')
    assert response.status_code == 200
    assert response.data['user']['email'] == 'test@example.com'
    assert len(response.data['roles']) > 0


@pytest.mark.django_db
def test_logout(api_client, user):
    """Test logout returns 204"""
    api_client.force_authenticate(user=user)
    response = api_client.post('/api/auth/logout')
    assert response.status_code == 204

