"""
Frameworks views
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import FrameworkCandidate, Framework
from .serializers import FrameworkCandidateSerializer, FrameworkSerializer
from core.permissions import IsOrgAdmin


class FrameworkCandidateViewSet(viewsets.ModelViewSet):
    queryset = FrameworkCandidate.objects.all()
    serializer_class = FrameworkCandidateSerializer
    permission_classes = [IsOrgAdmin]

    @action(detail=False, methods=['post'], url_path='ingest')
    def ingest(self, request):
        """Ingest framework from whitelisted source"""
        source = request.data.get('source')
        source_type = request.data.get('source_type', 'whitelisted_source')
        
        # TODO: Fetch and parse framework from source
        # For now, create a candidate with raw data
        candidate = FrameworkCandidate.objects.create(
            source=source,
            source_type=source_type,
            name=request.data.get('name', 'Unknown Framework'),
            description=request.data.get('description', ''),
            raw_data=request.data.get('raw_data', {}),
            status='PENDING'
        )
        
        serializer = self.get_serializer(candidate)
        return Response(serializer.data)

    @action(detail=True, methods=['post'], url_path='approve')
    def approve(self, request, pk=None):
        """Approve candidate and create Framework"""
        candidate = self.get_object()
        
        if candidate.status != 'PENDING':
            return Response(
                {'error': 'Candidate already reviewed'},
                status=status.HTTP_400_BAD_REQUEST
            )
        
        # Create Framework from candidate
        framework = Framework.objects.create(
            candidate=candidate,
            name=candidate.name,
            description=candidate.description,
            slots=candidate.raw_data.get('slots', []),
            rules=candidate.raw_data.get('rules', []),
            prompts=candidate.raw_data.get('prompts', {}),
            output_schema=candidate.raw_data.get('output_schema', {}),
            category=candidate.raw_data.get('category', ''),
            tags=candidate.raw_data.get('tags', []),
        )
        
        candidate.status = 'APPROVED'
        candidate.save()
        
        serializer = FrameworkSerializer(framework)
        return Response(serializer.data)


class FrameworkViewSet(viewsets.ModelViewSet):
    queryset = Framework.objects.filter(is_active=True)
    serializer_class = FrameworkSerializer
    permission_classes = []  # Public read, admin write

