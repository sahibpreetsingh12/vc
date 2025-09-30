"""
Speech Agent - Converts audio input to text.

This agent is the entry point of the pipeline.
"""

from typing import Any, Dict, Optional
from .base import Agent, AgentResult


class SpeechAgent(Agent):
    """
    Converts spoken voice input into text commands.
    
    Uses STT tools (Google Cloud Speech-to-Text or Groq Whisper).
    """
    
    def __init__(self):
        super().__init__(
            name="Speech Agent",
            description="Converts voice audio to text using STT APIs"
        )
    
    def execute(self, input_data: Any, context: Optional[Dict] = None) -> AgentResult:
        """
        Convert audio to text.
        
        Args:
            input_data: Audio file path or audio bytes
            context: Optional context dict
            
        Returns:
            AgentResult with transcribed text
        """
        try:
            # Check if we have an STT tool
            if not self.tools:
                return AgentResult(
                    success=False,
                    data=None,
                    error="No STT tool configured"
                )
            
            # Use the first STT tool (could be Google or Groq)
            stt_tool = self.tools[0]
            result = stt_tool.call(input_data)
            
            if not result.success:
                return AgentResult(
                    success=False,
                    data=None,
                    error=f"STT failed: {result.error}"
                )
            
            transcript = result.output
            
            return AgentResult(
                success=True,
                data=transcript,
                metadata={
                    "agent": self.name,
                    "tool_used": stt_tool.name,
                    "audio_length": result.metadata.get("duration", "unknown")
                }
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data=None,
                error=f"Speech agent error: {str(e)}"
            )