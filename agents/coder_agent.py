"""
Coder Agent - Generates code from execution plan.

Translates the plan into actual source code.
"""

import re

from typing import Any, Dict, Optional
from .base import Agent, AgentResult


class CoderAgent(Agent):
    """
    Generates source code from execution plan.
    
    Uses LLM tools (Gemini, Groq) to write actual code.
    Also uses formatter tools to ensure code quality.
    """
    
    def __init__(self):
        super().__init__(
            name="Coder Agent",
            description="Generates code from execution plan"
        )
    
    def execute(self, input_data: Any, context: Optional[Dict] = None) -> AgentResult:
        """
        Generate code from the plan.
        
        Args:
            input_data: Dict with 'command' and 'steps' from reasoning agent
            context: Optional context (file path, existing code, language, etc.)
            
        Returns:
            AgentResult with generated code
        """
        try:
            if not isinstance(input_data, dict):
                return AgentResult(
                    success=False,
                    data=None,
                    error="Invalid input format (expected dict with 'steps')"
                )
            
            command = input_data.get("command", "")
            steps = input_data.get("steps", [])
            
            if not self.tools:
                return AgentResult(
                    success=False,
                    data=None,
                    error="No code generation tool configured"
                )
            
            # Use LLM tool for code generation
            codegen_tool = self.tools[0]
            
            prompt = self._build_codegen_prompt(command, steps, context)
            result = codegen_tool.call(prompt)
            
            if not result.success:
                return AgentResult(
                    success=False,
                    data=None,
                    error=f"Code generation failed: {result.error}"
                )
            
            generated_code = result.output
            
            # Clean up the code (remove markdown code blocks)
            generated_code = self._extract_code(generated_code, context.get("language", "python") if context else "python")
            
            # Optionally format the code
            if len(self.tools) > 1:
                formatter_tool = self.tools[1]
                format_result = formatter_tool.call(generated_code)
                if format_result.success:
                    generated_code = format_result.output
            
            # Generate a meaningful filename from the command
            suggested_filename = self._generate_filename(command, context.get("language", "python") if context else "python")
            
            return AgentResult(
                success=True,
                data={
                    "code": generated_code,
                    "language": context.get("language", "python") if context else "python",
                    "command": command,
                    "suggested_filename": suggested_filename
                },
                metadata={
                    "agent": self.name,
                    "tool_used": codegen_tool.name,
                    "formatted": len(self.tools) > 1
                }
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data=None,
                error=f"Coder agent error: {str(e)}"
            )
    
    def _build_codegen_prompt(self, command: str, steps: list, context: Optional[Dict]) -> str:
        """Build the LLM prompt for code generation."""
        language = context.get("language", "python") if context else "python"
        existing_code = context.get("existing_code", "") if context else ""
        
        prompt = f"""You are an expert {language} programmer. Generate ONLY working, production-ready code.

User Request: {command}

{"Existing Code to Modify:" if existing_code else ""}
{existing_code if existing_code else ""}

Generate complete, working {language} code that:
- Implements the exact user request
- Includes all necessary imports
- Has proper error handling
- Includes clear docstrings/comments
- Uses best practices for {language}
- Is ready to run without modifications

IMPORTANT: Return ONLY the code, no explanations, no markdown formatting, just pure code."""
        
        return prompt
    
    def _extract_code(self, text: str, language: str) -> str:
        """Extract code from LLM response, removing markdown and explanations."""
        # Try to extract code from markdown code blocks
        code_block_pattern = rf"```(?:{language})?\s*\n(.*?)```"
        matches = re.findall(code_block_pattern, text, re.DOTALL)
        
        if matches:
            # Return the first code block found
            return matches[0].strip()
        
        # If no code blocks, try to clean up the text
        # Remove common explanatory phrases
        lines = text.split('\n')
        code_lines = []
        in_code = False
        
        for line in lines:
            # Skip lines that look like explanations
            if line.strip().startswith(('Here', 'This', 'The', 'Note:', 'Explanation:')):
                continue
            # Skip lines with markdown backticks
            if '```' in line:
                in_code = not in_code
                continue
            # Add code lines
            if in_code or (line.strip() and not line.strip().startswith('#')):
                code_lines.append(line)
        
        return '\n'.join(code_lines).strip() if code_lines else text.strip()
    
    def _format_steps(self, steps: list) -> str:
        """Format steps for the prompt."""
        return "\n".join(f"{i+1}. {step}" for i, step in enumerate(steps))
    
    def _generate_filename(self, command: str, language: str) -> str:
        """Generate a concise, meaningful filename from the command."""
        import re
        
        # Extension mapping
        ext_map = {
            'python': 'py',
            'javascript': 'js',
            'typescript': 'ts',
            'html': 'html',
            'css': 'css',
            'java': 'java',
            'go': 'go',
            'rust': 'rs',
            'cpp': 'cpp',
            'c': 'c'
        }
        ext = ext_map.get(language, 'txt')
        
        # Extract key nouns/concepts from command
        command_lower = command.lower()
        
        # Common patterns to extract filename
        patterns = [
            # "create a user authentication module" -> "user_auth"
            r'create\s+(?:a\s+)?(?:an\s+)?(.+?)\s+(?:module|class|function|script|file|component)',
            # "build a calculator" -> "calculator"
            r'build\s+(?:a\s+)?(?:an\s+)?(.+?)(?:\s+that|\s+to|\s+which|$)',
            # "make a todo list" -> "todo_list"
            r'make\s+(?:a\s+)?(?:an\s+)?(.+?)(?:\s+that|\s+to|\s+which|$)',
            # "write a function to process data" -> "process_data"
            r'write\s+(?:a\s+)?(?:an\s+)?(?:function|method|class)\s+to\s+(.+?)(?:\s+that|\s+which|$)',
            # "add a login feature" -> "login"
            r'add\s+(?:a\s+)?(?:an\s+)?(.+?)\s+(?:feature|functionality|capability)',
            # "implement user registration" -> "user_registration"
            r'implement\s+(.+?)(?:\s+that|\s+to|\s+which|$)',
            # Generic: extract main subject
            r'(?:for|to)\s+(.+?)(?:\s+that|\s+to|\s+which|$)',
        ]
        
        filename = None
        for pattern in patterns:
            match = re.search(pattern, command_lower)
            if match:
                filename = match.group(1).strip()
                break
        
        # If no pattern matched, extract key nouns
        if not filename:
            # Remove common words and extract remaining words
            stop_words = {'a', 'an', 'the', 'to', 'for', 'of', 'in', 'on', 'at', 'by', 'with', 'from', 'that', 'which', 'this', 'these', 'those', 'i', 'you', 'we', 'they', 'create', 'make', 'build', 'write', 'add', 'implement', 'develop'}
            words = re.findall(r'\w+', command_lower)
            key_words = [w for w in words if w not in stop_words and len(w) > 2]
            filename = '_'.join(key_words[:3]) if key_words else 'code'
        
        # Clean up the filename
        filename = re.sub(r'[^a-z0-9_]+', '_', filename)
        filename = re.sub(r'_+', '_', filename)  # Remove multiple underscores
        filename = filename.strip('_')  # Remove leading/trailing underscores
        
        # Limit length
        if len(filename) > 30:
            filename = filename[:30].rstrip('_')
        
        # If empty, use default
        if not filename:
            filename = 'generated_code'
        
        return f"{filename}.{ext}"
