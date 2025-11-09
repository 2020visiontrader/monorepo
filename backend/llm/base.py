"""Base LLM provider interface"""
from abc import ABC, abstractmethod


class LLMProvider(ABC):
    """Abstract base class for LLM providers"""
    
    @abstractmethod
    def complete(self, prompt: str, **kwargs) -> str:
        """Generate completion for prompt"""
        pass

    @abstractmethod
    def embed(self, text: str) -> list[float]:
        """Generate embeddings for text"""
        pass