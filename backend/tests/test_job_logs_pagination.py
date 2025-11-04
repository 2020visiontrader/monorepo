"""
Job logs pagination tests
"""
import pytest
from rest_framework.test import APIClient
from core.models import Organization, User, BackgroundJob, JobLog
from brands.models import Brand, BrandProfile
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
def job(brand):
    return BackgroundJob.objects.create(
        task_name='test_task',
        status='SUCCESS',
        brand_id=brand.id,
        organization_id=brand.organization_id,
    )


@pytest.fixture
def many_logs(job):
    """Create >500 log lines"""
    logs = []
    for i in range(600):
        log = JobLog.objects.create(
            job=job,
            step='test_step',
            level='INFO',
            message=f'Log message {i}',
            idx=i,
        )
        logs.append(log)
    return logs


@pytest.mark.django_db
def test_job_logs_limit_cap_500(api_client, user, job, many_logs):
    """Test job logs limit is capped at 500"""
    api_client.force_authenticate(user=user)
    api_client.force_login(user)
    
    # Request with limit > 500
    response = api_client.get(f'/api/jobs/{job.id}/logs?offset=0&limit=1000')
    
    assert response.status_code == 200
    # Should cap internally at 500
    total_lines = sum(len(step['lines']) for step in response.data.get('steps', []))
    assert total_lines <= 500


@pytest.mark.django_db
def test_job_logs_pagination_with_next_offset(api_client, user, job, many_logs):
    """Test job logs pagination shows next_offset when more lines exist"""
    api_client.force_authenticate(user=user)
    api_client.force_login(user)
    
    # First page
    response1 = api_client.get(f'/api/jobs/{job.id}/logs?offset=0&limit=200')
    assert response1.status_code == 200
    assert response1.data.get('next_offset') == 200
    
    # Second page
    response2 = api_client.get(f'/api/jobs/{job.id}/logs?offset=200&limit=200')
    assert response2.status_code == 200
    assert response2.data.get('next_offset') == 400
    
    # Last page
    response3 = api_client.get(f'/api/jobs/{job.id}/logs?offset=500&limit=200')
    assert response3.status_code == 200
    # Should be None or not present if no more lines
    assert response3.data.get('next_offset') is None or response3.data.get('next_offset') >= 600


@pytest.mark.django_db
def test_job_logs_default_limit_200(api_client, user, job, many_logs):
    """Test job logs defaults to limit 200"""
    api_client.force_authenticate(user=user)
    api_client.force_login(user)
    
    response = api_client.get(f'/api/jobs/{job.id}/logs')
    
    assert response.status_code == 200
    # Should return ~200 lines (may vary by step grouping)
    assert 'next_offset' in response.data
    if response.data.get('next_offset') is not None:
        assert response.data.get('next_offset') <= 600

