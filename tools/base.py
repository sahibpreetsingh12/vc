"""
Base Tool abstraction.

Tools are the APIs that agents can call (STT, LLM, sanitizer, etc.)
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from dataclasses import dataclass


@dataclass
class ToolResult:
    """Standard result format for all tools."""
    success: bool
    output: Any
    error: Optional[str] = None
    metadata: Dict[str, Any] = None
    
    def __post_init__(self):
        if self.metadata is None:
            self.metadata = {}


class Tool(ABC):
    """
    Base Tool class.
    
    Tools encapsulate external APIs and services.
    Each tool should do one thing (STT, code gen, validation, etc.)
    """
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    @abstractmethod
    def call(self, input_data: Any, **kwargs) -> ToolResult:
        """
        Execute the tool's function.
        
        Args:
            input_data: The input for this tool
            **kwargs: Additional parameters specific to the tool
            
        Returns:
            ToolResult with success status and output
        """
        pass
    
    def __repr__(self):
        return f"{self.__class__.__name__}(name='{self.name}')"