"""
Brand views
"""
from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Brand, BrandProfile, Pathway
from .serializers import BrandSerializer, BrandProfileSerializer, PathwaySerializer
from core.permissions import IsBrandManager


class BrandViewSet(viewsets.ModelViewSet):
    queryset = Brand.objects.all()
    serializer_class = BrandSerializer
    permission_classes = [IsBrandManager]

    def get_queryset(self):
        org_id = self.request.org_id
        if org_id:
            return Brand.objects.filter(organization_id=org_id)
        return Brand.objects.none()

    @action(detail=True, methods=['post'], url_path='onboarding')
    def onboarding(self, request, pk=None):
        """Save brand profile from onboarding wizard"""
        brand = self.get_object()
        profile, created = BrandProfile.objects.get_or_create(brand=brand)
        
        serializer = BrandProfileSerializer(
            profile,
            data=request.data,
            partial=True
        )
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class PathwayViewSet(viewsets.ModelViewSet):
    queryset = Pathway.objects.all()
    serializer_class = PathwaySerializer
    permission_classes = [IsBrandManager]

    def get_queryset(self):
        brand_id = self.request.brand_id
        if brand_id:
            return Pathway.objects.filter(brand_id=brand_id)
        return Pathway.objects.none()

