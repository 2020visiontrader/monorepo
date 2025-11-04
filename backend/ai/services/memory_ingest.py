"""
Memory ingestion service for AI frameworks
"""
from typing import Dict, Any, List
from ai.models import BrandMemory
import logging

logger = logging.getLogger(__name__)


def ingest_memory(
    brand_id: str,
    memory_type: str,
    content: Dict[str, Any],
) -> BrandMemory:
    """
    Ingest memory for brand AI context
    """
    try:
        memory = BrandMemory.objects.create(
            brand_id=brand_id,
            memory_type=memory_type,
            content=content,
        )
        return memory
    except Exception as e:
        logger.error(f"Error ingesting memory: {e}", exc_info=True)
        raise


def get_brand_memories(
    brand_id: str,
    memory_type: str = None,
) -> List[BrandMemory]:
    """
    Get memories for a brand
    """
    try:
        queryset = BrandMemory.objects.filter(brand_id=brand_id)
        if memory_type:
            queryset = queryset.filter(memory_type=memory_type)
        return list(queryset.order_by('-created_at'))
    except Exception as e:
        logger.error(f"Error getting memories: {e}", exc_info=True)
        return []

