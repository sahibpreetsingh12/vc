"""
Security Agent - Validates and sanitizes commands.

Protects against prompt injection and malicious instructions.
"""

from typing import Any, Dict, Optional
from .base import Agent, AgentResult


class SecurityAgent(Agent):
    """
    Validates user commands for safety.
    
    Uses sanitizer tools to check for:
    - Prompt injection attempts
    - Malicious operations
    - Unsafe file access patterns
    """
    
    def __init__(self):
        super().__init__(
            name="Security Agent",
            description="Validates and sanitizes user commands"
        )
    
    def execute(self, input_data: Any, context: Optional[Dict] = None) -> AgentResult:
        """
        Validate and sanitize the command.
        
        Args:
            input_data: Text command from speech agent
            context: Optional context dict
            
        Returns:
            AgentResult with sanitized command or rejection
        """
        try:
            command = str(input_data).strip()
            
            if not command:
                return AgentResult(
                    success=False,
                    data=None,
                    error="Empty command"
                )
            
            # Use sanitizer tool if available
            if self.tools:
                sanitizer_tool = self.tools[0]
                result = sanitizer_tool.call(command)
                
                if not result.success:
                    return AgentResult(
                        success=False,
                        data=None,
                        error=f"Command rejected: {result.error}",
                        metadata={"original_command": command}
                    )
                
                sanitized_command = result.output
            else:
                # Basic sanitization if no tool
                sanitized_command = self._basic_sanitize(command)
            
            return AgentResult(
                success=True,
                data=sanitized_command,
                metadata={
                    "agent": self.name,
                    "original_command": command,
                    "sanitized": sanitized_command != command
                }
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data=None,
                error=f"Security agent error: {str(e)}"
            )
    
    def _basic_sanitize(self, command: str) -> str:
        """Basic sanitization without external tool."""
        # Remove dangerous patterns
        dangerous_keywords = [
            "rm -rf /",
            "sudo",
            "delete system",
            "drop database",
            "> /dev/null"
        ]
        
        lower_command = command.lower()
        for keyword in dangerous_keywords:
            if keyword in lower_command:
                raise ValueError(f"Dangerous keyword detected: {keyword}")
        
        return command