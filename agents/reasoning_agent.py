"""
Reasoning Agent - Plans execution steps.

Translates natural language commands into structured execution plans.
"""

from typing import Any, Dict, Optional, List
from .base import Agent, AgentResult


class ReasoningAgent(Agent):
    """
    Plans the execution steps for a command.
    
    Uses LLM to break down commands into actionable steps.
    Example:
        Input: "Create a function to fetch weather data"
        Output: [
            "Import requests library",
            "Define function fetch_weather(city)",
            "Make API call to weather service",
            "Parse and return JSON response"
        ]
    """
    
    def __init__(self):
        super().__init__(
            name="Reasoning Agent",
            description="Plans execution steps from natural language"
        )
    
    def execute(self, input_data: Any, context: Optional[Dict] = None) -> AgentResult:
        """
        Create an execution plan.
        
        Args:
            input_data: Sanitized command from security agent
            context: Optional context dict (may include file context, etc.)
            
        Returns:
            AgentResult with list of execution steps
        """
        try:
            command = str(input_data).strip()
            
            if not self.tools:
                # Fallback to simple parsing if no LLM tool
                steps = self._simple_plan(command)
            else:
                # Use LLM tool to create sophisticated plan
                llm_tool = self.tools[0]
                
                prompt = self._build_planning_prompt(command, context)
                result = llm_tool.call(prompt)
                
                if not result.success:
                    return AgentResult(
                        success=False,
                        data=None,
                        error=f"Planning failed: {result.error}"
                    )
                
                steps = self._parse_plan(result.output)
            
            return AgentResult(
                success=True,
                data={
                    "command": command,
                    "steps": steps,
                    "step_count": len(steps)
                },
                metadata={
                    "agent": self.name,
                    "planning_method": "llm" if self.tools else "simple"
                }
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data=None,
                error=f"Reasoning agent error: {str(e)}"
            )
    
    def _build_planning_prompt(self, command: str, context: Optional[Dict]) -> str:
        """Build the LLM prompt for planning."""
        language = context.get('language', 'python') if context else 'python'
        existing_code = context.get('existing_code', '') if context else ''
        
        prompt = f"""You are an expert software architect. Analyze this coding request and create a clear implementation plan.

User Request: {command}

Language: {language}
{"Existing Code: " + existing_code if existing_code else ""}

Create a concise, numbered list of 4-8 specific implementation steps. Be technical and actionable.
Focus on WHAT needs to be done, not HOW (the coder will handle the HOW).

Example format:
1. [Specific step]
2. [Specific step]
...

Steps:"""
        return prompt
    
    def _parse_plan(self, llm_output: str) -> List[str]:
        """Parse the LLM output into a list of steps."""
        lines = llm_output.strip().split('\n')
        steps = []
        
        for line in lines:
            line = line.strip()
            if line and (line[0].isdigit() or line.startswith('-') or line.startswith('•')):
                # Remove numbering/bullets
                step = line.lstrip('0123456789.-•) ').strip()
                if step:
                    steps.append(step)
        
        return steps if steps else [llm_output.strip()]
    
    def _simple_plan(self, command: str) -> List[str]:
        """Fallback: simple rule-based planning."""
        command_lower = command.lower()
        
        if "function" in command_lower or "def" in command_lower:
            return [
                "Define function signature",
                "Implement function body",
                "Add error handling",
                "Add docstring"
            ]
        elif "class" in command_lower:
            return [
                "Define class structure",
                "Add __init__ method",
                "Implement class methods",
                "Add docstrings"
            ]
        else:
            return [
                "Analyze command intent",
                "Generate appropriate code",
                "Add necessary imports",
                "Format and validate"
            ]