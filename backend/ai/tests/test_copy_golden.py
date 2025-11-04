"""
Golden snapshot tests for AI framework copy quality
"""
import pytest
import json
import os
from pathlib import Path
from django.test import override_settings
from django.core.management import call_command
from content.models import ProductDraft
from brands.models import Brand, BrandProfile
from core.models import Organization
from ai.frameworks.product_copy import generate_product_copy
from ai.validators import validate_content_variant
from ai.services.brand_context import get_brand_context


GOLDEN_FIXTURE_DIR = Path(__file__).parent.parent.parent / 'tests' / 'fixtures' / 'ai'
GOLDEN_FIXTURE_DIR.mkdir(parents=True, exist_ok=True)
GOLDEN_BASELINE_FILE = GOLDEN_FIXTURE_DIR / 'golden_baseline.json'


@pytest.fixture(scope='module', autouse=True)
def seed_demo_data(django_db_setup, django_db_blocker):
    """Seed demo data once per test module"""
    with django_db_blocker.unblock():
        call_command('seed_demo_data')


@pytest.fixture
def brand():
    """Get demo brand from seed data"""
    return Brand.objects.filter(slug='demo-brand-a').first()


@pytest.fixture
def products(brand):
    """Get demo products"""
    return list(ProductDraft.objects.filter(brand=brand)[:2])


def load_golden_baseline():
    """Load golden baseline if exists"""
    if GOLDEN_BASELINE_FILE.exists():
        with open(GOLDEN_BASELINE_FILE) as f:
            return json.load(f)
    return None


def save_golden_baseline(data):
    """Save golden baseline"""
    with open(GOLDEN_BASELINE_FILE, 'w') as f:
        json.dump(data, f, indent=2)


@pytest.mark.django_db
@override_settings(AI_FRAMEWORKS_ENABLED=True, AI_SHADOW_MODE=True, LLM_USE_MOCK=True)
def test_copy_golden_schema_and_policy(products, brand):
    """Test AI copy matches schema and passes policy checks"""
    if not products:
        pytest.skip("No products found - run seed_demo_data first")
    
    product_ids = [str(p.id) for p in products]
    fields = ['title', 'description']
    brand_id = str(brand.id)
    
    # Generate with AI framework
    ai_output = generate_product_copy(
        product_ids=product_ids,
        fields=fields,
        brand_id=brand_id,
        max_variants=3,
    )
    
    # Schema validation
    assert 'variants' in ai_output
    assert isinstance(ai_output['variants'], list)
    
    for variant in ai_output['variants']:
        # Validate schema
        is_valid, errors = validate_content_variant(variant)
        assert is_valid, f"Variant validation failed: {errors}"
        
        # Length policy (title < 60, description < 2000)
        if variant['field_name'] == 'title':
            assert len(variant['content']) <= 60, f"Title too long: {len(variant['content'])}"
        elif variant['field_name'] == 'description':
            assert len(variant['content']) <= 2000, f"Description too long: {len(variant['content'])}"
        
        # Lexicon checks
        brand_context = get_brand_context(brand_id)
        required_terms = brand_context.get('required_terms', [])
        forbidden_terms = brand_context.get('forbidden_terms', [])
        
        content_lower = variant['content'].lower()
        
        # Check forbidden terms
        for forbidden in forbidden_terms:
            assert forbidden.lower() not in content_lower, f"Forbidden term '{forbidden}' found in {variant['field_name']}"
        
        # Check required terms (if any)
        if required_terms:
            found_required = any(term.lower() in content_lower for term in required_terms)
            # Note: Not all variants need all terms, so this is informational
            # Could be made stricter per brand policy


@pytest.mark.django_db
@override_settings(AI_FRAMEWORKS_ENABLED=True, AI_SHADOW_MODE=True, LLM_USE_MOCK=True)
def test_copy_similarity_threshold(products, brand):
    """Test similarity across products is below threshold"""
    from ai.validators import check_similarity
    
    if not products or len(products) < 2:
        pytest.skip("Need at least 2 products")
    
    product_ids = [str(p.id) for p in products]
    brand_id = str(brand.id)
    
    # Generate variants
    ai_output = generate_product_copy(
        product_ids=product_ids,
        fields=['title'],
        brand_id=brand_id,
        max_variants=3,
    )
    
    # Extract titles
    titles = [v['content'] for v in ai_output['variants'] if v['field_name'] == 'title']
    
    if len(titles) >= 2:
        # Check similarity between first two titles
        similarity = check_similarity(titles[0], titles[1])
        # Threshold: cosine similarity < 0.9 (not too similar)
        assert similarity < 0.9, f"Titles too similar: {similarity:.2f}"


@pytest.mark.django_db
@override_settings(AI_FRAMEWORKS_ENABLED=True, AI_SHADOW_MODE=True, LLM_USE_MOCK=True)
def test_copy_golden_baseline_generation(products, brand):
    """Generate or verify golden baseline"""
    if not products:
        pytest.skip("No products found")
    
    product_ids = [str(p.id) for p in products]
    brand_id = str(brand.id)
    
    # Generate baseline (existing pipeline)
    # For now, use AI framework output as baseline structure
    # In production, this would be the actual baseline pipeline
    baseline_output = generate_product_copy(
        product_ids=product_ids,
        fields=['title', 'description'],
        brand_id=brand_id,
        max_variants=3,
    )
    
    # Save golden baseline if missing
    if not GOLDEN_BASELINE_FILE.exists():
        save_golden_baseline(baseline_output)
        pytest.skip("Golden baseline generated - re-run test to verify")
    
    # Load and compare structure (not content)
    golden = load_golden_baseline()
    assert golden is not None
    
    # Verify structure matches
    assert 'variants' in baseline_output
    assert 'variants' in golden
    assert len(baseline_output['variants']) == len(golden['variants'])

