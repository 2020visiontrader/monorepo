"""
Tests for per-framework flags
"""
import pytest
from django.test import override_settings
from ai.services.framework_flags import (
    get_framework_flag,
    is_framework_enabled,
    is_framework_shadow,
    should_use_mock,
)


@pytest.mark.django_db
@override_settings(
    AI_FRAMEWORKS_ENABLED=False,
    AI_SHADOW_MODE=True,
    AI_FRAMEWORKS_ENABLED_BY_NAME={'seo': True},
    AI_SHADOW_MODE_BY_NAME={'seo': False},
)
def test_seo_enabled_while_others_disabled():
    """Test SEO can be enabled while others stay disabled"""
    # SEO should be enabled
    assert is_framework_enabled('seo') is True
    assert is_framework_shadow('seo') is False  # Live mode
    
    # Others should be disabled (fallback to global)
    assert is_framework_enabled('product_copy') is False
    assert is_framework_enabled('blueprint') is False


@pytest.mark.django_db
@override_settings(
    AI_FRAMEWORKS_ENABLED=True,
    AI_SHADOW_MODE=True,
    AI_SHADOW_MODE_BY_NAME={'seo': False},
)
def test_seo_live_while_others_shadow():
    """Test SEO can be live while others stay shadow"""
    # SEO should be live
    assert is_framework_shadow('seo') is False
    
    # Others should be shadow (fallback to global)
    assert is_framework_shadow('product_copy') is True
    assert is_framework_shadow('blueprint') is True


@pytest.mark.django_db
@override_settings(
    AI_USE_MOCK_BY_FRAMEWORK={'product_copy': False, 'seo': True},
    LLM_USE_MOCK=True,
)
def test_per_framework_mock_settings():
    """Test per-framework mock settings"""
    # Product copy should use real (not mock)
    assert should_use_mock('product_copy') is False
    
    # SEO should use mock
    assert should_use_mock('seo') is True
    
    # Blueprint should fallback to global (LLM_USE_MOCK)
    assert should_use_mock('blueprint') is True


@pytest.mark.django_db
@override_settings(
    AI_FRAMEWORKS_ENABLED=False,
    AI_FRAMEWORKS_ENABLED_BY_NAME={},
)
def test_default_behavior_unchanged():
    """Test default behavior is unchanged when no per-framework flags set"""
    # All should be disabled (global default)
    assert is_framework_enabled('product_copy') is False
    assert is_framework_enabled('seo') is False
    assert is_framework_enabled('blueprint') is False

