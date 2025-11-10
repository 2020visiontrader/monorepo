"""
Authentication views
"""
from rest_framework import status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.response import Response
from rest_framework.permissions import AllowAny, IsAuthenticated
from django.contrib.auth import authenticate, login, logout
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from django.db import transaction
from django.utils.text import slugify
from .models import User, RoleAssignment, Organization, Role
from .serializers import UserSerializer, RoleAssignmentSerializer
from brands.models import Brand, BrandProfile


@api_view(['POST'])
@permission_classes([AllowAny])
def signup_view(request):
    """User signup with organization, brand, and onboarding creation"""
    email = request.data.get('email')
    password = request.data.get('password')
    name = request.data.get('name', '').strip()
    organization_name = request.data.get('organization_name', '').strip()
    brand_name = request.data.get('brand_name', '').strip()
    
    if not all([email, password, name, organization_name, brand_name]):
        return Response(
            {'detail': 'All fields are required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    if User.objects.filter(email=email).exists():
        return Response(
            {'detail': 'Email already registered'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    # Create everything in a transaction
    try:
        with transaction.atomic():
            # 1. Create organization
            org_slug = slugify(organization_name)
            organization = Organization.objects.create(
                name=organization_name,
                slug=org_slug
            )
            
            # 2. Create user
            user = User.objects.create_user(
                username=email,
                email=email,
                password=password,
                first_name=name.split()[0],
                last_name=' '.join(name.split()[1:]) if len(name.split()) > 1 else '',
                organization=organization
            )
            
            # 3. Create brand
            brand_slug = slugify(brand_name)
            brand = Brand.objects.create(
                organization=organization,
                name=brand_name,
                slug=brand_slug
            )
            
            # 4. Create role assignment (org admin)
            RoleAssignment.objects.create(
                user=user,
                organization=organization,
                role=Role.ORG_ADMIN
            )

            # 5. Create brand role assignment
            RoleAssignment.objects.create(
                user=user,
                organization=organization,
                brand_id=brand.id,
                role=Role.BRAND_MANAGER
            )

            # 6. Create brand profile with onboarding state using get_or_create for idempotency
            from django.db import IntegrityError
            try:
                brand_profile, created = BrandProfile.objects.get_or_create(
                    brand=brand,
                    defaults={
                        'onboarding_step': 'mission',
                        'completed_steps': [],
                        'is_onboarding_complete': False,
                        'owner': user,
                    }
                )
                if not created:
                    # Update fields carefully without overwriting existing data
                    updated = False
                    if brand_profile.owner is None:
                        brand_profile.owner = user
                        updated = True
                    if updated:
                        brand_profile.save(update_fields=['owner'])
            except IntegrityError:
                # Handle rare race condition - fetch existing profile
                brand_profile = BrandProfile.objects.get(brand=brand)
                if brand_profile.owner is None:
                    brand_profile.owner = user
                    brand_profile.save(update_fields=['owner'])
            
            # Log user in
            login(request, user)
            
            return Response({
                'user': UserSerializer(user).data,
                'organization': {
                    'id': str(organization.id),
                    'name': organization.name,
                    'slug': organization.slug
                },
                'brand': {
                    'id': str(brand.id),
                    'name': brand.name,
                    'slug': brand.slug,
                    'onboarding': {
                        'current_step': brand_profile.onboarding_step,
                        'next_steps': brand_profile.next_steps,
                        'is_complete': brand_profile.is_onboarding_complete
                    }
                }
            }, status=status.HTTP_201_CREATED)
            
    except Exception as e:
        return Response(
            {'detail': str(e)},
            status=status.HTTP_400_BAD_REQUEST
        )


@api_view(['POST'])
@permission_classes([AllowAny])
def login_view(request):
    """User login"""
    email = request.data.get('email')
    password = request.data.get('password')
    
    if not email or not password:
        return Response(
            {'detail': 'Email and password required'},
            status=status.HTTP_400_BAD_REQUEST
        )
    
    try:
        user = User.objects.get(email=email)
    except User.DoesNotExist:
        return Response(
            {'detail': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    user = authenticate(request, username=user.username, password=password)
    if user is None:
        return Response(
            {'detail': 'Invalid credentials'},
            status=status.HTTP_401_UNAUTHORIZED
        )
    
    login(request, user)
    
    # Get user's roles and brands
    roles = RoleAssignment.objects.filter(user=user)
    orgs = [role.organization for role in roles if role.organization]
    brands = []
    for role in roles:
        if role.brand_id:
            from brands.models import Brand
            try:
                brands.append(Brand.objects.get(id=role.brand_id))
            except Brand.DoesNotExist:
                pass
    
    return Response({
        'user': UserSerializer(user).data,
        'roles': [RoleAssignmentSerializer(role).data for role in roles],
        'orgs': [{'id': str(org.id), 'name': org.name} for org in orgs],
        'brands': [{'id': str(brand.id), 'name': brand.name} for brand in brands],
    })


@api_view(['POST'])
@permission_classes([IsAuthenticated])
def logout_view(request):
    """User logout"""
    logout(request)
    return Response(status=status.HTTP_204_NO_CONTENT)


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def me_view(request):
    """Get current user info"""
    user = request.user
    roles = RoleAssignment.objects.filter(user=user)
    orgs = [role.organization for role in roles if role.organization]
    brands = []
    for role in roles:
        if role.brand_id:
            from brands.models import Brand
            try:
                brands.append(Brand.objects.get(id=role.brand_id))
            except Brand.DoesNotExist:
                pass
    
    return Response({
        'user': UserSerializer(user).data,
        'roles': [RoleAssignmentSerializer(role).data for role in roles],
        'orgs': [{'id': str(org.id), 'name': org.name} for org in orgs],
        'brands': [{'id': str(brand.id), 'name': brand.name} for brand in brands],
    })
