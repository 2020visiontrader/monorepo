"""
Change recommendations framework
Matches existing response shapes
"""
from typing import Dict, Any
from ai.providers.abacus_provider import get_ai_provider
import logging

logger = logging.getLogger(__name__)


def analyze_changes(
    before: Dict[str, Any],
    after: Dict[str, Any],
) -> Dict[str, Any]:
    """
    Analyze changes and provide recommendations
    Returns shape matching existing recommendation structure
    """
    try:
        provider = get_ai_provider()
        analysis = provider.analyze_changes(before, after)
        
        return {
            'summary': analysis.get('summary', ''),
            'fields_changed': analysis.get('fields_changed', []),
            'confidence': analysis.get('confidence', 0.0),
            'recommendations': analysis.get('recommendations', []),
            'framework': 'ai_change_recs',
        }
    except Exception as e:
        logger.error(f"AI framework change_recs failed: {e}", exc_info=True)
        raise

