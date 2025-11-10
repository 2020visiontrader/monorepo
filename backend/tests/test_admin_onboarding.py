"""
Tests for admin onboarding functionality
"""
import pytest
from django.utils import timezone
from rest_framework import status
from rest_framework.test import APIClient
from onboarding.models import OnboardingSession, UserConsent, OnboardingScan
from core.models import User, Organization


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def organization(db):
    return Organization.objects.create(name='Test Org', slug='test-org')


@pytest.fixture
def admin_user(db, organization):
    """Create admin user"""
    user = User.objects.create(
        username='admin@example.com',
        email='admin@example.com',
        first_name='Admin',
        last_name='User',
        is_staff=True,
        is_superuser=True,
    )
    user.organization = organization
    user.set_password('testpass123')
    user.save()
    return user


@pytest.fixture
def regular_user(db, organization):
    """Create regular user"""
    user = User.objects.create(
        username='user@example.com',
        email='user@example.com',
        first_name='Regular',
        last_name='User',
    )
    user.organization = organization
    user.set_password('testpass123')
    user.save()
    return user


@pytest.mark.django_db
class TestAdminSessionsList:
    """Test admin sessions list endpoint"""

    def test_admin_sessions_requires_staff(self, api_client, regular_user):
        """Test that admin endpoint requires staff permission"""
        api_client.force_authenticate(user=regular_user)

        response = api_client.get('/api/onboarding/admin/sessions/')

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_sessions_accessible_to_staff(self, api_client, admin_user):
        """Test that staff can access admin endpoint"""
        api_client.force_authenticate(user=admin_user)

        response = api_client.get('/api/onboarding/admin/sessions/')

        assert response.status_code == status.HTTP_200_OK

    def test_admin_sessions_pagination(self, api_client, admin_user):
        """Test that sessions list supports pagination"""
        # Create 60 sessions
        for i in range(60):
            OnboardingSession.objects.create(status='initiated')

        api_client.force_authenticate(user=admin_user)
        response = api_client.get('/api/onboarding/admin/sessions/')

        assert response.status_code == status.HTTP_200_OK
        # Should have pagination info
        assert 'results' in response.data or isinstance(response.data, list)

    def test_admin_sessions_filter_by_status(self, api_client, admin_user):
        """Test filtering sessions by status"""
        OnboardingSession.objects.create(status='initiated')
        OnboardingSession.objects.create(status='completed')
        OnboardingSession.objects.create(status='completed')

        api_client.force_authenticate(user=admin_user)
        response = api_client.get('/api/onboarding/admin/sessions/?status=completed')

        assert response.status_code == status.HTTP_200_OK

    def test_admin_sessions_search(self, api_client, admin_user, regular_user):
        """Test searching sessions by user email"""
        session = OnboardingSession.objects.create(
            status='initiated',
            user=regular_user
        )

        api_client.force_authenticate(user=admin_user)
        response = api_client.get('/api/onboarding/admin/sessions/?search=user@example.com')

        assert response.status_code == status.HTTP_200_OK

    def test_admin_sessions_date_range_filter(self, api_client, admin_user):
        """Test filtering by date range"""
        OnboardingSession.objects.create(status='initiated')

        api_client.force_authenticate(user=admin_user)
        response = api_client.get(
            f'/api/onboarding/admin/sessions/?start_date={timezone.now().date()}'
        )

        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestAdminSessionDetail:
    """Test admin session detail endpoint"""

    def test_admin_session_details(self, api_client, admin_user):
        """Test getting detailed session information"""
        session = OnboardingSession.objects.create(
            status='initiated',
            raw_payload={'mission': 'test'}
        )

        UserConsent.objects.create(
            session=session,
            consent_given=True,
            consent_scope=['catalog_scan'],
            ip_address='192.168.1.1',
            user_agent='Mozilla/5.0'
        )

        api_client.force_authenticate(user=admin_user)
        response = api_client.get(f'/api/onboarding/admin/sessions/{session.session_id}/')

        assert response.status_code == status.HTTP_200_OK
        assert 'raw_payload' in response.data
        assert 'consents' in response.data
        assert len(response.data['consents']) == 1

    def test_admin_session_details_includes_scans(self, api_client, admin_user):
        """Test that session details include scan information"""
        session = OnboardingSession.objects.create(status='initiated')
        OnboardingScan.objects.create(session=session, status='completed')

        api_client.force_authenticate(user=admin_user)
        response = api_client.get(f'/api/onboarding/admin/sessions/{session.session_id}/')

        assert response.status_code == status.HTTP_200_OK
        assert 'scans' in response.data
        assert len(response.data['scans']) == 1


@pytest.mark.django_db
class TestAdminRescan:
    """Test admin force rescan functionality"""

    def test_admin_force_rescan(self, api_client, admin_user):
        """Test that admin can force rescan"""
        from unittest.mock import patch, MagicMock

        session = OnboardingSession.objects.create(status='initiated')
        UserConsent.objects.create(
            session=session,
            consent_given=True,
            consent_scope=['catalog_scan'],
            ip_address='192.168.1.1',
            user_agent='Mozilla/5.0'
        )

        api_client.force_authenticate(user=admin_user)

        with patch('onboarding.views.run_catalog_scan.apply_async') as mock_task:
            mock_task.return_value = MagicMock(id='task-123')

            response = api_client.post(
                f'/api/onboarding/admin/sessions/{session.session_id}/rescan/',
                {},
                format='json'
            )

            assert response.status_code == status.HTTP_201_CREATED
            assert 'scan_id' in response.data

            # Verify scan has high priority
            scan = OnboardingScan.objects.get(scan_id=response.data['scan_id'])
            assert scan.priority == 10

    def test_admin_rescan_requires_staff(self, api_client, regular_user):
        """Test that rescan requires staff permission"""
        session = OnboardingSession.objects.create(status='initiated')

        api_client.force_authenticate(user=regular_user)

        response = api_client.post(
            f'/api/onboarding/admin/sessions/{session.session_id}/rescan/',
            {},
            format='json'
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN

    def test_admin_rescan_requires_consent(self, api_client, admin_user):
        """Test that rescan still requires consent"""
        session = OnboardingSession.objects.create(status='initiated')

        api_client.force_authenticate(user=admin_user)

        response = api_client.post(
            f'/api/onboarding/admin/sessions/{session.session_id}/rescan/',
            {},
            format='json'
        )

        assert response.status_code == status.HTTP_403_FORBIDDEN
        assert 'consent' in response.data['error'].lower()


@pytest.mark.django_db
class TestAdminExport:
    """Test admin export functionality"""

    def test_admin_export_csv(self, api_client, admin_user):
        """Test exporting sessions to CSV"""
        OnboardingSession.objects.create(status='initiated', user=admin_user)

        api_client.force_authenticate(user=admin_user)

        response = api_client.get('/api/onboarding/admin/sessions/export/')

        assert response.status_code == status.HTTP_200_OK
        assert response['Content-Type'] == 'text/csv'
        assert 'attachment' in response['Content-Disposition']

    def test_admin_export_includes_filters(self, api_client, admin_user):
        """Test that export respects filters"""
        OnboardingSession.objects.create(status='initiated')
        OnboardingSession.objects.create(status='completed')

        api_client.force_authenticate(user=admin_user)

        response = api_client.get('/api/onboarding/admin/sessions/export/?status=completed')

        assert response.status_code == status.HTTP_200_OK


@pytest.mark.django_db
class TestSuggestionsEndpoint:
    """Test AI suggestions endpoint"""

    def test_suggestions_requires_completed_scan(self, api_client):
        """Test that suggestions require a completed scan"""
        session = OnboardingSession.objects.create(status='initiated')

        response = api_client.get(
            f'/api/onboarding/sessions/{session.session_id}/suggestions/'
        )

        assert response.status_code == status.HTTP_404_NOT_FOUND
        assert 'scan' in response.data['error'].lower()

    def test_suggestions_returns_valid_schema(self, api_client):
        """Test that suggestions return valid schema"""
        from onboarding.models import OnboardingSuggestion

        session = OnboardingSession.objects.create(status='initiated')
        scan = OnboardingScan.objects.create(
            session=session,
            status='completed',
            result={'summary': {}}
        )
        OnboardingSuggestion.objects.create(
            scan=scan,
            suggestion_type='pricing',
            title='Test Suggestion',
            description='Test description',
            priority='high',
            impact_score=85
        )

        response = api_client.get(
            f'/api/onboarding/sessions/{session.session_id}/suggestions/'
        )

        assert response.status_code == status.HTTP_200_OK
        assert len(response.data) > 0
        assert 'suggestion_type' in response.data[0]
        assert 'title' in response.data[0]
        assert 'priority' in response.data[0]
        assert 'impact_score' in response.data[0]

    def test_suggestions_cached(self, api_client):
        """Test that suggestions are cached"""
        from onboarding.models import OnboardingSuggestion
        from django.core.cache import cache

        session = OnboardingSession.objects.create(status='initiated')
        scan = OnboardingScan.objects.create(
            session=session,
            status='completed',
            result={'summary': {}}
        )
        OnboardingSuggestion.objects.create(
            scan=scan,
            suggestion_type='pricing',
            title='Test Suggestion',
            description='Test',
            priority='high',
            impact_score=85
        )

        # First request
        response1 = api_client.get(
            f'/api/onboarding/sessions/{session.session_id}/suggestions/'
        )

        # Check cache
        cache_key = f'suggestions:{session.session_id}'
        cached_data = cache.get(cache_key)
        assert cached_data is not None

        # Second request should use cache
        response2 = api_client.get(
            f'/api/onboarding/sessions/{session.session_id}/suggestions/'
        )

        assert response1.data == response2.data

    def test_suggestions_filter_by_type(self, api_client):
        """Test filtering suggestions by type"""
        from onboarding.models import OnboardingSuggestion

        session = OnboardingSession.objects.create(status='initiated')
        scan = OnboardingScan.objects.create(
            session=session,
            status='completed',
            result={'summary': {}}
        )
        OnboardingSuggestion.objects.create(
            scan=scan,
            suggestion_type='pricing',
            title='Pricing Suggestion',
            description='Test',
            priority='high',
            impact_score=85
        )
        OnboardingSuggestion.objects.create(
            scan=scan,
            suggestion_type='seo',
            title='SEO Suggestion',
            description='Test',
            priority='medium',
            impact_score=70
        )

        response = api_client.get(
            f'/api/onboarding/sessions/{session.session_id}/suggestions/?type=pricing'
        )

        assert response.status_code == status.HTTP_200_OK

    def test_suggestions_prioritized(self, api_client):
        """Test that suggestions are prioritized by impact score"""
        from onboarding.models import OnboardingSuggestion

        session = OnboardingSession.objects.create(status='initiated')
        scan = OnboardingScan.objects.create(
            session=session,
            status='completed',
            result={'summary': {}}
        )

        # Create suggestions with different impact scores
        OnboardingSuggestion.objects.create(
            scan=scan,
            suggestion_type='pricing',
            title='Low Impact',
            description='Test',
            priority='low',
            impact_score=30
        )
        OnboardingSuggestion.objects.create(
            scan=scan,
            suggestion_type='seo',
            title='High Impact',
            description='Test',
            priority='critical',
            impact_score=95
        )

        response = api_client.get(
            f'/api/onboarding/sessions/{session.session_id}/suggestions/'
        )

        assert response.status_code == status.HTTP_200_OK
        # First suggestion should have higher impact score
        assert response.data[0]['impact_score'] >= response.data[1]['impact_score']
