"""
Tests for onboarding session management
"""
import pytest
from django.utils import timezone
from datetime import timedelta
from rest_framework import status
from rest_framework.test import APIClient
from onboarding.models import OnboardingSession
from core.models import User, Organization
from brands.models import Brand


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def organization(db):
    return Organization.objects.create(name='Test Org', slug='test-org')


@pytest.fixture
def user(db, organization):
    user = User.objects.create(
        username='test@example.com',
        email='test@example.com',
        first_name='Test',
        last_name='User',
    )
    user.organization = organization
    user.set_password('testpass123')
    user.save()
    return user


@pytest.fixture
def brand(db, organization):
    return Brand.objects.create(
        name='Test Brand',
        slug='test-brand',
        organization=organization
    )


@pytest.mark.django_db
class TestOnboardingSessionCreation:
    """Test session creation and initialization"""

    def test_start_session_creates_uuid(self, api_client):
        """Test that starting a session creates a UUID"""
        response = api_client.post('/api/onboarding/sessions/', {})

        assert response.status_code == status.HTTP_201_CREATED
        assert 'session_id' in response.data
        assert response.data['status'] == 'initiated'

    def test_start_session_creates_db_record(self, api_client):
        """Test that session is persisted to database"""
        response = api_client.post('/api/onboarding/sessions/', {})

        session_id = response.data['session_id']
        session = OnboardingSession.objects.get(session_id=session_id)

        assert session is not None
        assert session.status == 'initiated'

    def test_authenticated_user_session_linked(self, api_client, user):
        """Test that authenticated user is linked to session"""
        api_client.force_authenticate(user=user)
        response = api_client.post('/api/onboarding/sessions/', {})

        session_id = response.data['session_id']
        session = OnboardingSession.objects.get(session_id=session_id)

        assert session.user == user

    def test_anonymous_user_session_allowed(self, api_client):
        """Test that anonymous users can create sessions"""
        response = api_client.post('/api/onboarding/sessions/', {})

        assert response.status_code == status.HTTP_201_CREATED
        session = OnboardingSession.objects.get(session_id=response.data['session_id'])
        assert session.user is None

    def test_session_has_expiry(self, api_client):
        """Test that session has expiry set"""
        response = api_client.post('/api/onboarding/sessions/', {})

        assert response.data['expires_at'] is not None

    def test_session_metadata_captured(self, api_client):
        """Test that session captures user agent and IP"""
        response = api_client.post('/api/onboarding/sessions/', {
            'user_agent': 'Mozilla/5.0',
            'ip_address': '192.168.1.1'
        })

        session = OnboardingSession.objects.get(session_id=response.data['session_id'])
        assert session.user_agent == 'Mozilla/5.0'
        assert session.ip_address == '192.168.1.1'


@pytest.mark.django_db
class TestOnboardingSessionRetrieval:
    """Test session retrieval"""

    def test_retrieve_session_by_id(self, api_client):
        """Test retrieving session by session_id"""
        # Create session
        response = api_client.post('/api/onboarding/sessions/', {})
        session_id = response.data['session_id']

        # Retrieve session
        response = api_client.get(f'/api/onboarding/sessions/{session_id}/')

        assert response.status_code == status.HTTP_200_OK
        assert response.data['session_id'] == session_id

    def test_invalid_session_returns_404(self, api_client):
        """Test that invalid session ID returns 404"""
        response = api_client.get('/api/onboarding/sessions/00000000-0000-0000-0000-000000000000/')

        assert response.status_code == status.HTTP_404_NOT_FOUND

    def test_expired_session_returns_410(self, api_client):
        """Test that expired session returns 410 Gone"""
        # Create session and manually expire it
        session = OnboardingSession.objects.create(
            status='initiated',
            expires_at=timezone.now() - timedelta(hours=1)
        )

        response = api_client.get(f'/api/onboarding/sessions/{session.session_id}/')

        assert response.status_code == status.HTTP_410_GONE
        assert 'expired' in response.data['error'].lower()


@pytest.mark.django_db
class TestOnboardingSessionUpdates:
    """Test updating session answers"""

    def test_save_answers_merges_payload(self, api_client):
        """Test that saving answers merges into raw_payload"""
        # Create session
        response = api_client.post('/api/onboarding/sessions/', {})
        session_id = response.data['session_id']

        # Save first step
        response = api_client.patch(
            f'/api/onboarding/sessions/{session_id}/answers/',
            {
                'step': 'mission',
                'data': {'mission': 'To sell great products'}
            },
            format='json'
        )

        assert response.status_code == status.HTTP_200_OK

        # Verify payload
        session = OnboardingSession.objects.get(session_id=session_id)
        assert 'mission' in session.raw_payload
        assert session.raw_payload['mission']['mission'] == 'To sell great products'

    def test_save_answers_updates_completed_steps(self, api_client):
        """Test that completed_steps is updated"""
        response = api_client.post('/api/onboarding/sessions/', {})
        session_id = response.data['session_id']

        api_client.patch(
            f'/api/onboarding/sessions/{session_id}/answers/',
            {
                'step': 'mission',
                'data': {'mission': 'Test'}
            },
            format='json'
        )

        session = OnboardingSession.objects.get(session_id=session_id)
        assert 'mission' in session.completed_steps

    def test_save_answers_changes_status_to_in_progress(self, api_client):
        """Test that saving answers changes status"""
        response = api_client.post('/api/onboarding/sessions/', {})
        session_id = response.data['session_id']

        api_client.patch(
            f'/api/onboarding/sessions/{session_id}/answers/',
            {
                'step': 'mission',
                'data': {'mission': 'Test'}
            },
            format='json'
        )

        session = OnboardingSession.objects.get(session_id=session_id)
        assert session.status == 'in_progress'

    def test_resume_session_returns_saved_data(self, api_client):
        """Test that resuming session returns previously saved data"""
        # Create and update session
        response = api_client.post('/api/onboarding/sessions/', {})
        session_id = response.data['session_id']

        api_client.patch(
            f'/api/onboarding/sessions/{session_id}/answers/',
            {
                'step': 'mission',
                'data': {'mission': 'Test Mission'}
            },
            format='json'
        )

        # Retrieve session
        response = api_client.get(f'/api/onboarding/sessions/{session_id}/')

        assert response.data['raw_payload']['mission']['mission'] == 'Test Mission'
        assert 'mission' in response.data['completed_steps']

    def test_expired_session_cannot_be_updated(self, api_client):
        """Test that expired sessions cannot be updated"""
        session = OnboardingSession.objects.create(
            status='initiated',
            expires_at=timezone.now() - timedelta(hours=1)
        )

        response = api_client.patch(
            f'/api/onboarding/sessions/{session.session_id}/answers/',
            {
                'step': 'mission',
                'data': {'mission': 'Test'}
            },
            format='json'
        )

        assert response.status_code == status.HTTP_410_GONE


@pytest.mark.django_db
class TestStoreSettingsValidation:
    """Test store settings validation"""

    def test_valid_store_settings_accepted(self, api_client):
        """Test that valid store settings are accepted"""
        response = api_client.post('/api/onboarding/sessions/', {})
        session_id = response.data['session_id']

        response = api_client.patch(
            f'/api/onboarding/sessions/{session_id}/answers/',
            {
                'step': 'store_settings',
                'data': {
                    'platform': 'shopify',
                    'store_url': 'https://example.myshopify.com'
                }
            },
            format='json'
        )

        assert response.status_code == status.HTTP_200_OK

    def test_invalid_url_rejected(self, api_client):
        """Test that invalid URLs are rejected"""
        response = api_client.post('/api/onboarding/sessions/', {})
        session_id = response.data['session_id']

        response = api_client.patch(
            f'/api/onboarding/sessions/{session_id}/answers/',
            {
                'step': 'store_settings',
                'data': {
                    'platform': 'shopify',
                    'store_url': 'not-a-url'
                }
            },
            format='json'
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_invalid_currency_rejected(self, api_client):
        """Test that invalid currency codes are rejected"""
        response = api_client.post('/api/onboarding/sessions/', {})
        session_id = response.data['session_id']

        response = api_client.patch(
            f'/api/onboarding/sessions/{session_id}/answers/',
            {
                'step': 'store_settings',
                'data': {
                    'platform': 'shopify',
                    'store_url': 'https://example.myshopify.com',
                    'currency': 'INVALID'
                }
            },
            format='json'
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
