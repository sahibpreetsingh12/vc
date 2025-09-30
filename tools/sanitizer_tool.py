"""
Sanitizer Tool - validates commands for safety.
"""

import re
from typing import Any
from .base import Tool, ToolResult
from config import settings


class SanitizerTool(Tool):
    """
    Sanitizes user commands to prevent malicious inputs.
    
    Checks for:
    - Dangerous shell commands
    - Prompt injection patterns
    - Unsafe file operations
    """
    
    # Dangerous patterns to block
    DANGEROUS_PATTERNS = [
        r"rm\s+-rf\s+/",
        r"sudo\s+",
        r"drop\s+database",
        r"delete\s+from\s+\*",
        r"exec\s*\(",
        r"eval\s*\(",
        r"__import__",
    ]
    
    # Prompt injection patterns
    INJECTION_PATTERNS = [
        r"ignore\s+previous\s+instructions",
        r"disregard\s+all\s+prior",
        r"system:\s+",
        r"<\|im_start\|>",
        r"<\|im_end\|>",
    ]
    
    def __init__(self):
        super().__init__(
            name="Command Sanitizer",
            description="Validates and sanitizes user commands"
        )
    
    def call(self, input_data: Any, **kwargs) -> ToolResult:
        """
        Sanitize a command.
        
        Args:
            input_data: Text command to sanitize
            
        Returns:
            ToolResult with sanitized command or error
        """
        try:
            command = str(input_data).strip()
            
            if not command:
                return ToolResult(
                    success=False,
                    output=None,
                    error="Empty command"
                )
            
            # Check for dangerous patterns
            for pattern in self.DANGEROUS_PATTERNS:
                if re.search(pattern, command, re.IGNORECASE):
                    return ToolResult(
                        success=False,
                        output=None,
                        error=f"Dangerous pattern detected: {pattern}"
                    )
            
            # Check for prompt injection
            for pattern in self.INJECTION_PATTERNS:
                if re.search(pattern, command, re.IGNORECASE):
                    return ToolResult(
                        success=False,
                        output=None,
                        error="Potential prompt injection detected"
                    )
            
            # Basic sanitization: remove suspicious characters
            sanitized = command
            # Remove multiple spaces
            sanitized = re.sub(r'\s+', ' ', sanitized)
            
            return ToolResult(
                success=True,
                output=sanitized,
                metadata={
                    "original": command,
                    "modified": sanitized != command
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                output=None,
                error=f"Sanitization error: {str(e)}"
            )