"""
Base AI provider interface
"""
from abc import ABC, abstractmethod
from typing import Dict, Any, Optional


class AIProvider(ABC):
    """Base interface for AI providers"""
    
    @abstractmethod
    def generate_content(self, prompt: str, context: Dict[str, Any], **kwargs) -> Dict[str, Any]:
        """Generate content given prompt and context"""
        pass
    
    @abstractmethod
    def generate_seo(self, page_data: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate SEO optimization"""
        pass
    
    @abstractmethod
    def generate_blueprint(self, requirements: Dict[str, Any], context: Dict[str, Any]) -> Dict[str, Any]:
        """Generate site blueprint"""
        pass
    
    @abstractmethod
    def analyze_changes(self, before: Dict[str, Any], after: Dict[str, Any]) -> Dict[str, Any]:
        """Analyze changes between two states"""
        pass

