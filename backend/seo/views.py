"""
SEO views
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import SEOPlan
from .serializers import SEOPlanSerializer
from core.permissions import IsEditorOrAbove
from .tasks import generate_seo_task


class SEOPlanViewSet(viewsets.ModelViewSet):
    queryset = SEOPlan.objects.all()
    serializer_class = SEOPlanSerializer
    permission_classes = [IsEditorOrAbove]

    def get_queryset(self):
        brand_id = self.request.brand_id
        if brand_id:
            return SEOPlan.objects.filter(brand_id=brand_id)
        return SEOPlan.objects.none()

    @action(detail=False, methods=['post'], url_path='generate')
    def generate(self, request):
        """Generate SEO optimization"""
        brand_id = request.brand_id
        if not brand_id:
            return Response({'error': 'Brand ID required'}, status=status.HTTP_400_BAD_REQUEST)
        
        scope = request.data.get('scope', 'all')
        items = request.data.get('items', [])
        
        # Trigger task
        task = generate_seo_task.delay(brand_id, scope, items)
        
        return Response({
            'task_id': task.id,
            'status': 'pending'
        })

