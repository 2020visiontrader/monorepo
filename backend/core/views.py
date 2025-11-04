"""
Core views
"""
from rest_framework import viewsets
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Organization, User, RoleAssignment, BackgroundJob
from .serializers import OrganizationSerializer, UserSerializer, RoleAssignmentSerializer
from .permissions import IsOrgAdmin


class OrganizationViewSet(viewsets.ModelViewSet):
    queryset = Organization.objects.all()
    serializer_class = OrganizationSerializer
    permission_classes = [IsOrgAdmin]

    def get_queryset(self):
        # Filter by user's organization
        if self.request.user.is_authenticated:
            return Organization.objects.filter(id=self.request.user.organization_id)
        return Organization.objects.none()


class UserViewSet(viewsets.ModelViewSet):
    queryset = User.objects.all()
    serializer_class = UserSerializer
    permission_classes = [IsOrgAdmin]


class BackgroundJobViewSet(viewsets.ReadOnlyModelViewSet):
    """View background job status"""
    queryset = BackgroundJob.objects.all()
    serializer_class = None  # TODO: Add serializer

    def retrieve(self, request, pk=None):
        try:
            job = BackgroundJob.objects.get(id=pk)
            return Response({
                'id': str(job.id),
                'task_id': job.task_id,
                'task_name': job.task_name,
                'status': job.status,
                'result': job.result,
                'error': job.error,
                'created_at': job.created_at,
                'updated_at': job.updated_at,
            })
        except BackgroundJob.DoesNotExist:
            return Response({'error': 'Job not found'}, status=404)

