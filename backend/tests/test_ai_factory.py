"""
Test factory for FrameworkRun entries
"""
import pytest
from ai.models import FrameworkRun
import uuid


@pytest.fixture
def framework_run_factory():
    """Factory for creating FrameworkRun test instances"""
    def _create_framework_run(
        brand_id=None,
        framework_name='product_copy',
        status='SUCCESS',
        is_shadow=True,
        **kwargs
    ):
        if brand_id is None:
            brand_id = uuid.uuid4()
        
        return FrameworkRun.objects.create(
            brand_id=brand_id,
            framework_name=framework_name,
            input_hash=FrameworkRun.hash_input(kwargs.get('input_data', {})),
            input_data=kwargs.get('input_data', {}),
            output_data=kwargs.get('output_data', {}),
            baseline_output=kwargs.get('baseline_output', {}),
            diff_summary=kwargs.get('diff_summary', {}),
            status=status,
            is_shadow=is_shadow,
            **{k: v for k, v in kwargs.items() if k not in ['input_data', 'output_data', 'baseline_output', 'diff_summary']}
        )
    
    return _create_framework_run


@pytest.mark.django_db
def test_framework_run_factory(framework_run_factory):
    """Test framework run factory creates valid instances"""
    run = framework_run_factory(
        framework_name='seo',
        status='SUCCESS',
        input_data={'page': 'test'},
        output_data={'title': 'SEO Title'},
    )
    
    assert run.framework_name == 'seo'
    assert run.status == 'SUCCESS'
    assert run.input_data == {'page': 'test'}
    assert run.output_data == {'title': 'SEO Title'}


@pytest.mark.django_db
def test_framework_run_hash_input():
    """Test input hashing for deduplication"""
    input1 = {'product_ids': ['1', '2'], 'fields': ['title']}
    input2 = {'fields': ['title'], 'product_ids': ['1', '2']}  # Same, different order
    
    hash1 = FrameworkRun.hash_input(input1)
    hash2 = FrameworkRun.hash_input(input2)
    
    # Should produce same hash regardless of key order
    assert hash1 == hash2

