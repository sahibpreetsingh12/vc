"""
Base Agent abstraction for the multi-agent system.

All agents inherit from this base class and implement the execute method.
"""

from abc import ABC, abstractmethod
from typing import Any, Dict, Optional
from dataclasses import dataclass
from datetime import datetime


@dataclass
class AgentResult:
    """Standard result format for all agents."""
    success: bool
    data: Any
    error: Optional[str] = None
    metadata: Dict[str, Any] = None
    timestamp: datetime = None
    
    def __post_init__(self):
        if self.timestamp is None:
            self.timestamp = datetime.now()
        if self.metadata is None:
            self.metadata = {}


class Agent(ABC):
    """
    Base Agent class following ReAct paradigm.
    
    Each agent:
    - Has a name and description
    - Can use multiple tools
    - Executes a single responsibility
    - Returns standardized results
    """
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.tools = []
    
    def add_tool(self, tool):
        """Register a tool that this agent can use."""
        self.tools.append(tool)
        return self
    
    @abstractmethod
    def execute(self, input_data: Any, context: Optional[Dict] = None) -> AgentResult:
        """
        Execute the agent's primary function.
        
        Args:
            input_data: The input for this agent (format varies by agent)
            context: Optional context dict for passing state between agents
            
        Returns:
            AgentResult with success status, data, and metadata
        """
        pass
    
    def __repr__(self):
        return f"{self.__class__.__name__}(name='{self.name}')"