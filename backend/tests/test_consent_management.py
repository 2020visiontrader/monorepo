"""
Tests for GDPR-compliant consent management
"""
import pytest
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from onboarding.models import OnboardingSession, UserConsent


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def session(db):
    """Create a test session"""
    return OnboardingSession.objects.create(status='initiated')


@pytest.mark.django_db
class TestConsentRecording:
    """Test consent recording functionality"""

    def test_consent_records_with_ip_and_timestamp(self, api_client, session):
        """Test that consent is recorded with IP and timestamp"""
        response = api_client.post(
            f'/api/onboarding/sessions/{session.session_id}/consent/',
            {
                'consent_given': True,
                'consent_scope': ['catalog_scan', 'analytics'],
                'ip_address': '192.168.1.1',
                'user_agent': 'Mozilla/5.0'
            },
            format='json'
        )

        assert response.status_code == status.HTTP_201_CREATED
        assert 'id' in response.data

        # Verify in database
        consent = UserConsent.objects.get(id=response.data['id'])
        assert consent.ip_address == '192.168.1.1'
        assert consent.user_agent == 'Mozilla/5.0'
        assert consent.timestamp is not None

    def test_consent_given_with_scope(self, api_client, session):
        """Test giving consent with specific scope"""
        response = api_client.post(
            f'/api/onboarding/sessions/{session.session_id}/consent/',
            {
                'consent_given': True,
                'consent_scope': ['catalog_scan'],
                'ip_address': '192.168.1.1',
                'user_agent': 'Mozilla/5.0'
            },
            format='json'
        )

        assert response.status_code == status.HTTP_201_CREATED

        consent = UserConsent.objects.get(id=response.data['id'])
        assert consent.consent_given is True
        assert 'catalog_scan' in consent.consent_scope

    def test_consent_declined(self, api_client, session):
        """Test declining consent"""
        response = api_client.post(
            f'/api/onboarding/sessions/{session.session_id}/consent/',
            {
                'consent_given': False,
                'consent_scope': [],
                'ip_address': '192.168.1.1',
                'user_agent': 'Mozilla/5.0'
            },
            format='json'
        )

        assert response.status_code == status.HTTP_201_CREATED

        consent = UserConsent.objects.get(id=response.data['id'])
        assert consent.consent_given is False

    def test_consent_requires_scope_when_given(self, api_client, session):
        """Test that scope is required when consent is given"""
        response = api_client.post(
            f'/api/onboarding/sessions/{session.session_id}/consent/',
            {
                'consent_given': True,
                'ip_address': '192.168.1.1',
                'user_agent': 'Mozilla/5.0'
            },
            format='json'
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_multiple_consent_records_allowed(self, api_client, session):
        """Test that multiple consent records can exist (e.g., for changes)"""
        # First consent
        api_client.post(
            f'/api/onboarding/sessions/{session.session_id}/consent/',
            {
                'consent_given': True,
                'consent_scope': ['catalog_scan'],
                'ip_address': '192.168.1.1',
                'user_agent': 'Mozilla/5.0'
            },
            format='json'
        )

        # Second consent (e.g., expanding scope)
        response = api_client.post(
            f'/api/onboarding/sessions/{session.session_id}/consent/',
            {
                'consent_given': True,
                'consent_scope': ['catalog_scan', 'analytics'],
                'ip_address': '192.168.1.1',
                'user_agent': 'Mozilla/5.0'
            },
            format='json'
        )

        assert response.status_code == status.HTTP_201_CREATED

        # Should have 2 consent records
        assert UserConsent.objects.filter(session=session).count() == 2


@pytest.mark.django_db
class TestConsentBlocking:
    """Test that consent blocks certain operations"""

    def test_scan_requires_consent(self, api_client, session):
        """Test that catalog scan requires consent"""
        response = api_client.post(
            f'/api/onboarding/sessions/{session.session_id}/scan/',
            {},
            format='json'
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert 'consent' in response.data['error'].lower()

    def test_scan_blocked_when_consent_declined(self, api_client, session):
        """Test that scan is blocked when consent is declined"""
        # Decline consent
        api_client.post(
            f'/api/onboarding/sessions/{session.session_id}/consent/',
            {
                'consent_given': False,
                'consent_scope': [],
                'ip_address': '192.168.1.1',
                'user_agent': 'Mozilla/5.0'
            },
            format='json'
        )

        # Try to scan
        response = api_client.post(
            f'/api/onboarding/sessions/{session.session_id}/scan/',
            {},
            format='json'
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_scan_allowed_when_consent_given(self, api_client, session):
        """Test that scan is allowed when consent is given"""
        # Give consent
        api_client.post(
            f'/api/onboarding/sessions/{session.session_id}/consent/',
            {
                'consent_given': True,
                'consent_scope': ['catalog_scan'],
                'ip_address': '192.168.1.1',
                'user_agent': 'Mozilla/5.0'
            },
            format='json'
        )

        # Try to scan
        response = api_client.post(
            f'/api/onboarding/sessions/{session.session_id}/scan/',
            {},
            format='json'
        )

        assert response.status_code == status.HTTP_201_CREATED


@pytest.mark.django_db
class TestConsentRevocation:
    """Test consent revocation"""

    def test_consent_can_be_revoked(self, session):
        """Test that consent can be revoked"""
        consent = UserConsent.objects.create(
            session=session,
            consent_given=True,
            consent_scope=['catalog_scan'],
            ip_address='192.168.1.1',
            user_agent='Mozilla/5.0'
        )

        consent.revoke_consent()

        assert consent.revoked is True
        assert consent.revoked_at is not None

    def test_revoked_consent_blocks_scan(self, api_client, session):
        """Test that revoked consent blocks scans"""
        # Create and revoke consent
        consent = UserConsent.objects.create(
            session=session,
            consent_given=True,
            consent_scope=['catalog_scan'],
            ip_address='192.168.1.1',
            user_agent='Mozilla/5.0'
        )
        consent.revoke_consent()

        # Try to scan
        response = api_client.post(
            f'/api/onboarding/sessions/{session.session_id}/scan/',
            {},
            format='json'
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN


@pytest.mark.django_db
class TestGDPRAuditTrail:
    """Test GDPR audit trail functionality"""

    def test_consent_has_audit_trail(self, session):
        """Test that all required audit fields are captured"""
        consent = UserConsent.objects.create(
            session=session,
            consent_given=True,
            consent_scope=['catalog_scan'],
            ip_address='192.168.1.1',
            user_agent='Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        )

        # Verify all audit fields
        assert consent.timestamp is not None
        assert consent.ip_address == '192.168.1.1'
        assert consent.user_agent == 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'
        assert consent.consent_given is True
        assert consent.consent_scope == ['catalog_scan']

    def test_consent_scope_checking(self, session):
        """Test checking for specific consent scopes"""
        consent = UserConsent.objects.create(
            session=session,
            consent_given=True,
            consent_scope=['catalog_scan', 'analytics'],
            ip_address='192.168.1.1',
            user_agent='Mozilla/5.0'
        )

        assert consent.has_scope('catalog_scan') is True
        assert consent.has_scope('analytics') is True
        assert consent.has_scope('marketing') is False

    def test_consent_history_preserved(self, session):
        """Test that consent history is preserved"""
        # Create multiple consent records
        UserConsent.objects.create(
            session=session,
            consent_given=True,
            consent_scope=['catalog_scan'],
            ip_address='192.168.1.1',
            user_agent='Mozilla/5.0'
        )

        UserConsent.objects.create(
            session=session,
            consent_given=True,
            consent_scope=['catalog_scan', 'analytics'],
            ip_address='192.168.1.1',
            user_agent='Mozilla/5.0'
        )

        # Both records should exist
        consents = UserConsent.objects.filter(session=session).order_by('timestamp')
        assert consents.count() == 2
        assert len(consents[0].consent_scope) == 1
        assert len(consents[1].consent_scope) == 2


@pytest.mark.django_db
class TestConsentValidation:
    """Test consent data validation"""

    def test_invalid_consent_scope_rejected(self, api_client, session):
        """Test that invalid consent scopes are rejected"""
        response = api_client.post(
            f'/api/onboarding/sessions/{session.session_id}/consent/',
            {
                'consent_given': True,
                'consent_scope': ['invalid_scope'],
                'ip_address': '192.168.1.1',
                'user_agent': 'Mozilla/5.0'
            },
            format='json'
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST

    def test_missing_required_fields_rejected(self, api_client, session):
        """Test that missing required fields are rejected"""
        response = api_client.post(
            f'/api/onboarding/sessions/{session.session_id}/consent/',
            {
                'consent_given': True,
                'consent_scope': ['catalog_scan']
                # Missing ip_address and user_agent
            },
            format='json'
        )

        assert response.status_code == status.HTTP_400_BAD_REQUEST
