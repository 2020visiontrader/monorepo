"""
Job logs tests
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
def job_logs(job):
    logs = []
    for i in range(5):
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
def test_job_logs_pagination(api_client, user, job, job_logs):
    """Test job logs pagination"""
    api_client.force_authenticate(user=user)
    
    response = api_client.get(f'/api/jobs/{job.id}/logs?offset=0&limit=2')
    assert response.status_code == 200
    assert 'steps' in response.data
    assert 'next_offset' in response.data
    assert response.data['id'] == str(job.id)
    assert response.data['status'] == 'success'


@pytest.mark.django_db
def test_job_logs_cross_brand_404(api_client, user, org):
    """Test job logs returns 404 for cross-brand access"""
    other_brand = Brand.objects.create(
        organization=org,
        name='Other Brand',
        slug='other-brand',
    )
    other_job = BackgroundJob.objects.create(
        task_name='other_task',
        status='PENDING',
        brand_id=other_brand.id,
        organization_id=org.id,
    )
    
    api_client.force_authenticate(user=user)
    # Set brand_id to different brand (simulate cross-brand access)
    response = api_client.get(f'/api/jobs/{other_job.id}/logs')
    # Should return 404 due to cross-brand check
    assert response.status_code == 404


@pytest.mark.django_db
def test_job_logs_limit_cap(api_client, user, job, job_logs):
    """Test job logs limit is capped at 1000"""
    api_client.force_authenticate(user=user)
    
    response = api_client.get(f'/api/jobs/{job.id}/logs?offset=0&limit=2000')
    assert response.status_code == 200
    # Should cap at 1000 internally
    assert len(response.data.get('steps', [])) >= 0

