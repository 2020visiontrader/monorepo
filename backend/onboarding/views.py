"""
Onboarding views
"""
from rest_framework import viewsets, status, permissions
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404
from django.utils import timezone
from django.db.models import Q
from django.core.cache import cache

from .models import OnboardingSession, UserConsent, OnboardingScan, OnboardingSuggestion
from .serializers import (
    OnboardingSessionSerializer,
    OnboardingSessionCreateSerializer,
    OnboardingSessionUpdateSerializer,
    UserConsentSerializer,
    UserConsentCreateSerializer,
    OnboardingScanSerializer,
    OnboardingScanCreateSerializer,
    OnboardingSuggestionSerializer,
    AdminSessionListSerializer,
    AdminSessionDetailSerializer
)
from .tasks import run_catalog_scan


class OnboardingSessionViewSet(viewsets.ModelViewSet):
    """
    ViewSet for managing onboarding sessions
    """
    queryset = OnboardingSession.objects.all()
    serializer_class = OnboardingSessionSerializer
    permission_classes = [permissions.AllowAny]  # Supports anonymous users
    lookup_field = 'session_id'

    def get_queryset(self):
        """Filter sessions based on user"""
        if self.request.user.is_authenticated:
            return OnboardingSession.objects.filter(
                Q(user=self.request.user) | Q(user__isnull=True)
            )
        return OnboardingSession.objects.filter(user__isnull=True)

    def create(self, request, *args, **kwargs):
        """
        Start a new onboarding session
        POST /api/onboarding/start
        """
        serializer = OnboardingSessionCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Create session
        session = OnboardingSession.objects.create(
            user=request.user if request.user.is_authenticated else None,
            user_agent=serializer.validated_data.get('user_agent', ''),
            ip_address=serializer.validated_data.get('ip_address'),
            brand_id=serializer.validated_data.get('brand_id'),
            status='initiated'
        )

        response_serializer = OnboardingSessionSerializer(session)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    def retrieve(self, request, session_id=None):
        """
        Get session details
        GET /api/onboarding/{session_id}
        """
        session = get_object_or_404(OnboardingSession, session_id=session_id)

        # Check if session is expired
        if session.is_expired():
            return Response(
                {'error': 'Session has expired'},
                status=status.HTTP_410_GONE
            )

        serializer = OnboardingSessionSerializer(session)
        return Response(serializer.data)

    @action(detail=True, methods=['patch'], url_path='answers')
    def update_answers(self, request, session_id=None):
        """
        Save incremental answers to session
        PATCH /api/onboarding/{session_id}/answers
        """
        session = get_object_or_404(OnboardingSession, session_id=session_id)

        # Check if session is expired
        if session.is_expired():
            return Response(
                {'error': 'Session has expired'},
                status=status.HTTP_410_GONE
            )

        serializer = OnboardingSessionUpdateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        step = serializer.validated_data['step']
        data = serializer.validated_data['data']

        # Update session
        session.update_payload({step: data})
        session.current_step = step

        if step not in session.completed_steps:
            session.completed_steps.append(step)

        session.save()

        response_serializer = OnboardingSessionSerializer(session)
        return Response(response_serializer.data)

    @action(detail=True, methods=['post'])
    def consent(self, request, session_id=None):
        """
        Record user consent
        POST /api/onboarding/{session_id}/consent
        """
        session = get_object_or_404(OnboardingSession, session_id=session_id)

        # Check if session is expired
        if session.is_expired():
            return Response(
                {'error': 'Session has expired'},
                status=status.HTTP_410_GONE
            )

        serializer = UserConsentCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Create consent record
        consent = UserConsent.objects.create(
            session=session,
            consent_given=serializer.validated_data['consent_given'],
            consent_scope=serializer.validated_data.get('consent_scope', []),
            ip_address=serializer.validated_data['ip_address'],
            user_agent=serializer.validated_data['user_agent']
        )

        response_serializer = UserConsentSerializer(consent)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['post'])
    def scan(self, request, session_id=None):
        """
        Initiate catalog scan
        POST /api/onboarding/{session_id}/scan
        """
        session = get_object_or_404(OnboardingSession, session_id=session_id)

        # Check if session is expired
        if session.is_expired():
            return Response(
                {'error': 'Session has expired'},
                status=status.HTTP_410_GONE
            )

        # Check consent
        has_consent = UserConsent.objects.filter(
            session=session,
            consent_given=True,
            revoked=False
        ).exists()

        if not has_consent:
            return Response(
                {'error': 'Consent required before initiating scan'},
                status=status.HTTP_403_FORBIDDEN
            )

        serializer = OnboardingScanCreateSerializer(data=request.data)
        serializer.is_valid(raise_exception=True)

        # Create scan record
        scan = OnboardingScan.objects.create(
            session=session,
            scan_config=serializer.validated_data.get('scan_config', {}),
            priority=serializer.validated_data.get('priority', 0),
            status='queued'
        )

        # Enqueue Celery task
        task = run_catalog_scan.apply_async(
            args=[str(scan.scan_id)],
            priority=scan.priority
        )
        scan.celery_task_id = task.id
        scan.save()

        response_serializer = OnboardingScanSerializer(scan)
        return Response(response_serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=True, methods=['get'], url_path='scan_status')
    def scan_status(self, request, session_id=None):
        """
        Get scan status
        GET /api/onboarding/{session_id}/scan_status
        """
        session = get_object_or_404(OnboardingSession, session_id=session_id)

        # Get most recent scan
        scan = session.scans.order_by('-created_at').first()

        if not scan:
            return Response(
                {'error': 'No scan found for this session'},
                status=status.HTTP_404_NOT_FOUND
            )

        serializer = OnboardingScanSerializer(scan)
        return Response(serializer.data)

    @action(detail=True, methods=['get'])
    def suggestions(self, request, session_id=None):
        """
        Get AI suggestions
        GET /api/onboarding/{session_id}/suggestions
        """
        session = get_object_or_404(OnboardingSession, session_id=session_id)

        # Check cache first
        cache_key = f'suggestions:{session_id}'
        cached_data = cache.get(cache_key)
        if cached_data:
            return Response(cached_data)

        # Get most recent completed scan
        scan = session.scans.filter(status='completed').order_by('-finished_at').first()

        if not scan:
            return Response(
                {'error': 'No completed scan found. Please run a scan first.'},
                status=status.HTTP_404_NOT_FOUND
            )

        # Get suggestions
        suggestions = OnboardingSuggestion.objects.filter(scan=scan)

        # Allow filtering by type and priority
        suggestion_type = request.query_params.get('type')
        priority = request.query_params.get('priority')

        if suggestion_type:
            suggestions = suggestions.filter(suggestion_type=suggestion_type)
        if priority:
            suggestions = suggestions.filter(priority=priority)

        serializer = OnboardingSuggestionSerializer(suggestions, many=True)

        # Cache for 24 hours
        cache.set(cache_key, serializer.data, 60 * 60 * 24)

        return Response(serializer.data)


class AdminOnboardingViewSet(viewsets.ReadOnlyModelViewSet):
    """
    Admin viewset for monitoring onboarding sessions
    """
    queryset = OnboardingSession.objects.all()
    serializer_class = AdminSessionListSerializer
    permission_classes = [permissions.IsAdminUser]
    lookup_field = 'session_id'

    def get_queryset(self):
        """
        Support filtering and search
        """
        queryset = OnboardingSession.objects.all()

        # Filter by status
        status_filter = self.request.query_params.get('status')
        if status_filter:
            queryset = queryset.filter(status=status_filter)

        # Filter by date range
        start_date = self.request.query_params.get('start_date')
        end_date = self.request.query_params.get('end_date')
        if start_date:
            queryset = queryset.filter(created_at__gte=start_date)
        if end_date:
            queryset = queryset.filter(created_at__lte=end_date)

        # Search by session_id or user email
        search = self.request.query_params.get('search')
        if search:
            queryset = queryset.filter(
                Q(session_id__icontains=search) |
                Q(user__email__icontains=search)
            )

        return queryset.order_by('-created_at')

    def retrieve(self, request, session_id=None):
        """
        Get detailed session information
        GET /api/admin/onboarding/sessions/{session_id}
        """
        session = get_object_or_404(OnboardingSession, session_id=session_id)
        serializer = AdminSessionDetailSerializer(session)
        return Response(serializer.data)

    @action(detail=True, methods=['post'])
    def rescan(self, request, session_id=None):
        """
        Force rescan for a session (admin only)
        POST /api/admin/onboarding/sessions/{session_id}/rescan
        """
        if not request.user.is_staff:
            raise PermissionDenied('Staff permission required')

        session = get_object_or_404(OnboardingSession, session_id=session_id)

        # Check consent
        has_consent = UserConsent.objects.filter(
            session=session,
            consent_given=True,
            revoked=False
        ).exists()

        if not has_consent:
            return Response(
                {'error': 'Cannot rescan: no valid consent'},
                status=status.HTTP_403_FORBIDDEN
            )

        # Create new scan with high priority
        scan = OnboardingScan.objects.create(
            session=session,
            scan_config=request.data.get('scan_config', {}),
            priority=10,  # High priority for admin rescans
            status='queued'
        )

        # Enqueue Celery task
        task = run_catalog_scan.apply_async(
            args=[str(scan.scan_id)],
            priority=scan.priority
        )
        scan.celery_task_id = task.id
        scan.save()

        # Log admin action
        # TODO: Add audit logging

        serializer = OnboardingScanSerializer(scan)
        return Response(serializer.data, status=status.HTTP_201_CREATED)

    @action(detail=False, methods=['get'])
    def export(self, request):
        """
        Export sessions to CSV
        GET /api/admin/onboarding/sessions/export
        """
        import csv
        from django.http import HttpResponse

        # Get filtered queryset
        queryset = self.get_queryset()

        # Create CSV response
        response = HttpResponse(content_type='text/csv')
        response['Content-Disposition'] = 'attachment; filename="onboarding_sessions.csv"'

        writer = csv.writer(response)
        writer.writerow([
            'Session ID', 'User Email', 'Brand', 'Status',
            'Current Step', 'Created At', 'Expires At'
        ])

        for session in queryset:
            writer.writerow([
                str(session.session_id),
                session.user.email if session.user else 'Anonymous',
                session.brand.name if session.brand else 'N/A',
                session.status,
                session.current_step,
                session.created_at.isoformat(),
                session.expires_at.isoformat() if session.expires_at else ''
            ])

        return response
