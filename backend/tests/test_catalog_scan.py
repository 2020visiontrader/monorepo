"""
Tests for catalog scan orchestration
"""
import pytest
from unittest.mock import patch, MagicMock
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from onboarding.models import OnboardingSession, UserConsent, OnboardingScan
from onboarding.tasks import run_catalog_scan


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def session_with_consent(db):
    """Create a session with valid consent"""
    session = OnboardingSession.objects.create(status='initiated')
    UserConsent.objects.create(
        session=session,
        consent_given=True,
        consent_scope=['catalog_scan'],
        ip_address='192.168.1.1',
        user_agent='Mozilla/5.0'
    )
    return session


@pytest.mark.django_db
class TestScanInitiation:
    """Test scan initiation"""

    def test_scan_creates_record(self, api_client, session_with_consent):
        """Test that initiating scan creates a record"""
        with patch('onboarding.views.run_catalog_scan.apply_async') as mock_task:
            mock_task.return_value = MagicMock(id='task-123')

            response = api_client.post(
                f'/api/onboarding/sessions/{session_with_consent.session_id}/scan/',
                {},
                format='json'
            )

            assert response.status_code == status.HTTP_201_CREATED
            assert 'scan_id' in response.data

            # Verify scan record
            scan = OnboardingScan.objects.get(scan_id=response.data['scan_id'])
            assert scan.session == session_with_consent
            assert scan.status == 'queued'

    def test_scan_enqueues_celery_task(self, api_client, session_with_consent):
        """Test that scan enqueues a Celery task"""
        with patch('onboarding.views.run_catalog_scan.apply_async') as mock_task:
            mock_task.return_value = MagicMock(id='task-123')

            response = api_client.post(
                f'/api/onboarding/sessions/{session_with_consent.session_id}/scan/',
                {},
                format='json'
            )

            assert mock_task.called
            scan = OnboardingScan.objects.get(scan_id=response.data['scan_id'])
            assert scan.celery_task_id == 'task-123'

    def test_scan_with_config(self, api_client, session_with_consent):
        """Test scan with custom configuration"""
        with patch('onboarding.views.run_catalog_scan.apply_async') as mock_task:
            mock_task.return_value = MagicMock(id='task-123')

            response = api_client.post(
                f'/api/onboarding/sessions/{session_with_consent.session_id}/scan/',
                {
                    'scan_config': {
                        'scan_depth': 'deep',
                        'timeout_seconds': 600
                    },
                    'priority': 5
                },
                format='json'
            )

            assert response.status_code == status.HTTP_201_CREATED

            scan = OnboardingScan.objects.get(scan_id=response.data['scan_id'])
            assert scan.scan_config['scan_depth'] == 'deep'
            assert scan.priority == 5


@pytest.mark.django_db
class TestScanStatus:
    """Test scan status monitoring"""

    def test_scan_status_queued(self, api_client, session_with_consent):
        """Test getting status of queued scan"""
        scan = OnboardingScan.objects.create(
            session=session_with_consent,
            status='queued'
        )

        response = api_client.get(
            f'/api/onboarding/sessions/{session_with_consent.session_id}/scan_status/'
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'queued'
        assert response.data['scan_id'] == str(scan.scan_id)

    def test_scan_status_running(self, api_client, session_with_consent):
        """Test getting status of running scan"""
        scan = OnboardingScan.objects.create(
            session=session_with_consent,
            status='running',
            progress_percentage=50,
            items_scanned=500,
            total_items=1000
        )

        response = api_client.get(
            f'/api/onboarding/sessions/{session_with_consent.session_id}/scan_status/'
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'running'
        assert response.data['progress_percentage'] == 50
        assert response.data['items_scanned'] == 500
        assert response.data['total_items'] == 1000

    def test_scan_status_completed(self, api_client, session_with_consent):
        """Test getting status of completed scan"""
        scan = OnboardingScan.objects.create(
            session=session_with_consent,
            status='completed',
            progress_percentage=100,
            result={'summary': {'total_products': 100}}
        )

        response = api_client.get(
            f'/api/onboarding/sessions/{session_with_consent.session_id}/scan_status/'
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'completed'
        assert response.data['progress_percentage'] == 100
        assert 'result' in response.data

    def test_scan_status_failed(self, api_client, session_with_consent):
        """Test getting status of failed scan"""
        scan = OnboardingScan.objects.create(
            session=session_with_consent,
            status='failed',
            error_message='Connection timeout'
        )

        response = api_client.get(
            f'/api/onboarding/sessions/{session_with_consent.session_id}/scan_status/'
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data['status'] == 'failed'
        assert response.data['error_message'] == 'Connection timeout'

    def test_no_scan_returns_404(self, api_client, session_with_consent):
        """Test that session with no scan returns 404"""
        response = api_client.get(
            f'/api/onboarding/sessions/{session_with_consent.session_id}/scan_status/'
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND


@pytest.mark.django_db
class TestScanProgression:
    """Test scan progression and updates"""

    def test_mark_scan_running(self):
        """Test marking scan as running"""
        scan = OnboardingScan.objects.create(
            session=OnboardingSession.objects.create(status='initiated'),
            status='queued'
        )

        scan.mark_running('celery-task-123')

        assert scan.status == 'running'
        assert scan.started_at is not None
        assert scan.celery_task_id == 'celery-task-123'

    def test_update_scan_progress(self):
        """Test updating scan progress"""
        scan = OnboardingScan.objects.create(
            session=OnboardingSession.objects.create(status='initiated'),
            status='running'
        )

        scan.update_progress(50, items_scanned=500, total_items=1000)

        assert scan.progress_percentage == 50
        assert scan.items_scanned == 500
        assert scan.total_items == 1000

    def test_mark_scan_completed(self):
        """Test marking scan as completed"""
        scan = OnboardingScan.objects.create(
            session=OnboardingSession.objects.create(status='initiated'),
            status='running'
        )

        result_data = {'summary': {'total_products': 100}}
        scan.mark_completed(result_data)

        assert scan.status == 'completed'
        assert scan.finished_at is not None
        assert scan.progress_percentage == 100
        assert scan.result == result_data

    def test_mark_scan_failed(self):
        """Test marking scan as failed"""
        scan = OnboardingScan.objects.create(
            session=OnboardingSession.objects.create(status='initiated'),
            status='running'
        )

        scan.mark_failed('Connection error')

        assert scan.status == 'failed'
        assert scan.finished_at is not None
        assert scan.error_message == 'Connection error'


@pytest.mark.django_db
class TestScanRetry:
    """Test scan retry logic"""

    def test_can_retry_when_under_max(self):
        """Test that scan can retry when under max retries"""
        scan = OnboardingScan.objects.create(
            session=OnboardingSession.objects.create(status='initiated'),
            status='failed',
            retry_count=0,
            max_retries=3
        )

        assert scan.can_retry() is True

    def test_cannot_retry_when_at_max(self):
        """Test that scan cannot retry when at max retries"""
        scan = OnboardingScan.objects.create(
            session=OnboardingSession.objects.create(status='initiated'),
            status='failed',
            retry_count=3,
            max_retries=3
        )

        assert scan.can_retry() is False

    def test_increment_retry_count(self):
        """Test incrementing retry count"""
        scan = OnboardingScan.objects.create(
            session=OnboardingSession.objects.create(status='initiated'),
            status='failed',
            retry_count=0
        )

        scan.increment_retry()

        assert scan.retry_count == 1


@pytest.mark.django_db
class TestScanTimeout:
    """Test scan timeout handling"""

    def test_scan_timeout_creates_timeout_status(self):
        """Test that timeout creates proper status"""
        scan = OnboardingScan.objects.create(
            session=OnboardingSession.objects.create(status='initiated'),
            status='running',
            retry_count=3,
            max_retries=3
        )

        # Simulate timeout
        scan.status = 'timeout'
        scan.error_message = 'Scan exceeded time limit'
        scan.finished_at = timezone.now()
        scan.save()

        assert scan.status == 'timeout'
        assert 'time limit' in scan.error_message


@pytest.mark.django_db
class TestProductPrioritiesValidation:
    """Test product priorities validation"""

    def test_product_priorities_validates_sku_limit(self, api_client, session_with_consent):
        """Test that SKU limit is enforced"""
        with patch('onboarding.views.run_catalog_scan.apply_async') as mock_task:
            mock_task.return_value = MagicMock(id='task-123')

            # Try with more than 1000 SKUs (should fail)
            skus = [f'SKU-{i}' for i in range(1001)]

            response = api_client.post(
                f'/api/onboarding/sessions/{session_with_consent.session_id}/scan/',
                {
                    'scan_config': {
                        'product_priorities': {
                            'selected_skus': skus
                        }
                    }
                },
                format='json'
            )

            assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_empty_sku_list_allowed(self, api_client, session_with_consent):
        """Test that empty SKU list is allowed"""
        with patch('onboarding.views.run_catalog_scan.apply_async') as mock_task:
            mock_task.return_value = MagicMock(id='task-123')

            response = api_client.post(
                f'/api/onboarding/sessions/{session_with_consent.session_id}/scan/',
                {
                    'scan_config': {
                        'product_priorities': {
                            'selected_skus': []
                        }
                    }
                },
                format='json'
            )

            # Empty list means scan all products
            assert response.status_code == status.HTTP_201_CREATED

    def test_duplicate_skus_rejected(self, api_client, session_with_consent):
        """Test that duplicate SKUs are rejected"""
        with patch('onboarding.views.run_catalog_scan.apply_async') as mock_task:
            mock_task.return_value = MagicMock(id='task-123')

            response = api_client.post(
                f'/api/onboarding/sessions/{session_with_consent.session_id}/scan/',
                {
                    'scan_config': {
                        'product_priorities': {
                            'selected_skus': ['SKU-1', 'SKU-1', 'SKU-2']
                        }
                    }
                },
                format='json'
            )

            assert response.status_code == status.HTTP_400_BAD_REQUEST


@pytest.mark.django_db
class TestScanOrchestration:
    """Test full scan orchestration"""

    def test_multiple_scans_allowed(self, api_client, session_with_consent):
        """Test that multiple scans can be created for same session"""
        with patch('onboarding.views.run_catalog_scan.apply_async') as mock_task:
            mock_task.return_value = MagicMock(id='task-123')

            # Create first scan
            api_client.post(
                f'/api/onboarding/sessions/{session_with_consent.session_id}/scan/',
                {},
                format='json'
            )

            # Create second scan
            response = api_client.post(
                f'/api/onboarding/sessions/{session_with_consent.session_id}/scan/',
                {},
                format='json'
            )

            assert response.status_code == status.HTTP_201_CREATED

            # Should have 2 scans
            scans = OnboardingScan.objects.filter(session=session_with_consent)
            assert scans.count() == 2

    def test_scan_status_returns_most_recent(self, api_client, session_with_consent):
        """Test that scan status returns most recent scan"""
        # Create two scans
        scan1 = OnboardingScan.objects.create(
            session=session_with_consent,
            status='completed'
        )

        scan2 = OnboardingScan.objects.create(
            session=session_with_consent,
            status='running'
        )

        response = api_client.get(
            f'/api/onboarding/sessions/{session_with_consent.session_id}/scan_status/'
        )

        assert response.status_code == status.HTTP_200_OK
        assert response.data['scan_id'] == str(scan2.scan_id)
