"""
Seed demo data command tests
"""
import pytest
from django.core.management import call_command
from core.models import Organization, User, RoleAssignment
from brands.models import Brand, BrandProfile
from content.models import ProductDraft
from competitors.models import CompetitorProfile


@pytest.mark.django_db
def test_seed_demo_data_command():
    """Test seed_demo_data command creates required data"""
    call_command('seed_demo_data')
    
    # Check organization
    org = Organization.objects.get(slug='demo-agency')
    assert org.name == 'Demo Agency'
    
    # Check users
    admin_user = User.objects.get(email='admin@demo.com')
    editor_user = User.objects.get(email='editor@demo.com')
    assert admin_user.check_password('password123!')
    assert editor_user.check_password('password123!')
    
    # Check roles
    admin_role = RoleAssignment.objects.get(user=admin_user, organization=org)
    assert admin_role.role == 'ORG_ADMIN'
    
    editor_role = RoleAssignment.objects.get(user=editor_user, organization=org)
    assert editor_role.role == 'EDITOR'
    
    # Check brands
    brand_a = Brand.objects.get(slug='demo-brand-a')
    brand_b = Brand.objects.get(slug='demo-brand-b')
    assert brand_a.name == 'Demo Brand A'
    assert brand_b.name == 'Demo Brand B'
    
    # Check profiles
    profile_a = BrandProfile.objects.get(brand=brand_a)
    profile_b = BrandProfile.objects.get(brand=brand_b)
    assert profile_a.single_sku is False
    assert profile_b.single_sku is True
    
    # Check products
    products_a = ProductDraft.objects.filter(brand=brand_a)
    products_b = ProductDraft.objects.filter(brand=brand_b)
    assert products_a.count() == 2
    assert products_b.count() == 2
    
    # Check competitors
    competitors = CompetitorProfile.objects.filter(brand__organization=org)
    assert competitors.count() >= 2


@pytest.mark.django_db
def test_seed_demo_data_idempotent():
    """Test seed_demo_data can be run multiple times safely"""
    call_command('seed_demo_data')
    first_count = Organization.objects.count()
    
    call_command('seed_demo_data')
    second_count = Organization.objects.count()
    
    assert first_count == second_count

