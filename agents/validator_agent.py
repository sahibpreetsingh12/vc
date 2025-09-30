"""
Validator Agent - Reviews, confirms, and applies code changes.

Last checkpoint before code is written to files (human-in-the-loop).
"""

from typing import Any, Dict, Optional
from .base import Agent, AgentResult


class ValidatorAgent(Agent):
    """
    Validates generated code and manages approval workflow.
    
    Responsibilities:
    1. Show diff preview
    2. Run basic validation (syntax, formatting)
    3. Request human approval
    4. Apply changes if approved
    """
    
    def __init__(self):
        super().__init__(
            name="Validator Agent",
            description="Validates code and manages approval workflow"
        )
    
    def execute(self, input_data: Any, context: Optional[Dict] = None) -> AgentResult:
        """
        Validate and potentially apply code changes.
        
        Args:
            input_data: Dict with 'code' from coder agent
            context: Optional context (file path, approval settings, etc.)
            
        Returns:
            AgentResult with validation status and applied changes
        """
        try:
            if not isinstance(input_data, dict):
                return AgentResult(
                    success=False,
                    data=None,
                    error="Invalid input format (expected dict with 'code')"
                )
            
            code = input_data.get("code", "")
            language = input_data.get("language", "python")
            command = input_data.get("command", "")
            
            # Step 1: Run validation tools
            validation_errors = []
            if self.tools:
                for tool in self.tools:
                    if "validator" in tool.name.lower() or "syntax" in tool.name.lower():
                        result = tool.call(code, language=language)
                        if not result.success:
                            validation_errors.append(result.error)
            
            if validation_errors:
                return AgentResult(
                    success=False,
                    data=None,
                    error=f"Validation failed: {'; '.join(validation_errors)}",
                    metadata={"validation_errors": validation_errors}
                )
            
            # Step 2: Create diff preview
            diff_preview = self._create_diff_preview(code, context)
            
            # Step 3: Check if approval is required
            require_approval = context.get("require_approval", True) if context else True
            
            if require_approval:
                # In a real implementation, this would show UI and wait for user input
                # For now, we return a "pending approval" state
                return AgentResult(
                    success=True,
                    data={
                        "status": "pending_approval",
                        "code": code,
                        "diff": diff_preview,
                        "command": command,
                        "language": language
                    },
                    metadata={
                        "agent": self.name,
                        "requires_approval": True,
                        "validated": True
                    }
                )
            else:
                # Auto-approve (not recommended for production)
                applied = self._apply_code(code, context)
                
                return AgentResult(
                    success=True,
                    data={
                        "status": "applied",
                        "code": code,
                        "file_path": context.get("file_path") if context else None,
                        "auto_approved": True
                    },
                    metadata={
                        "agent": self.name,
                        "applied": applied
                    }
                )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data=None,
                error=f"Validator agent error: {str(e)}"
            )
    
    def approve_and_apply(self, code: str, context: Optional[Dict] = None) -> AgentResult:
        """
        Explicitly approve and apply code (called after user approval).
        
        Args:
            code: The code to apply
            context: Context with file path, etc.
            
        Returns:
            AgentResult with application status
        """
        try:
            applied = self._apply_code(code, context)
            
            return AgentResult(
                success=applied,
                data={
                    "status": "applied",
                    "file_path": context.get("file_path") if context else None
                },
                metadata={"agent": self.name}
            )
        except Exception as e:
            return AgentResult(
                success=False,
                data=None,
                error=f"Failed to apply code: {str(e)}"
            )
    
    def _create_diff_preview(self, code: str, context: Optional[Dict]) -> str:
        """Create a diff preview of the changes."""
        if not context or "existing_code" not in context:
            return f"+ New code ({len(code.splitlines())} lines)"
        
        existing = context["existing_code"]
        # Simple diff (in real impl, use difflib)
        return f"~ Modified code\n  - {len(existing.splitlines())} lines\n  + {len(code.splitlines())} lines"
    
    def _apply_code(self, code: str, context: Optional[Dict]) -> bool:
        """Apply code to file (actual file I/O)."""
        if not context or "file_path" not in context:
            # No file path specified, just return success for demo
            return True
        
        file_path = context["file_path"]
        
        try:
            with open(file_path, 'w') as f:
                f.write(code)
            return True
        except Exception as e:
            print(f"Failed to write file: {e}")
            return False