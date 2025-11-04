"""
Health check tests
"""
import pytest
from rest_framework.test import APIClient


@pytest.fixture
def api_client():
    return APIClient()


@pytest.mark.django_db
def test_health_endpoint(api_client):
    """Test health endpoint returns ok=true"""
    response = api_client.get('/api/health')
    assert response.status_code == 200
    assert response.data['ok'] is True
    assert 'env' in response.data
    assert 'db' in response.data
    assert 'redis' in response.data

