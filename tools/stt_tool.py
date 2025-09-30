"""
Speech-to-Text (STT) Tool implementations.

Supports Google Cloud Speech-to-Text and Groq Whisper.
"""

from typing import Any
from .base import Tool, ToolResult
from config import settings


class GoogleSTTTool(Tool):
    """Google Cloud Speech-to-Text API wrapper - Real implementation."""
    
    def __init__(self):
        super().__init__(
            name="Google Cloud STT",
            description="Google Cloud Speech-to-Text API (SOTA)"
        )
        self.client = None
    
    def _get_client(self):
        """Lazy initialization of Google Speech client."""
        if self.client is None:
            try:
                from google.cloud import speech
                from config import settings
                import os
                
                # Set credentials if provided
                if settings.GOOGLE_APPLICATION_CREDENTIALS:
                    os.environ['GOOGLE_APPLICATION_CREDENTIALS'] = settings.GOOGLE_APPLICATION_CREDENTIALS
                
                self.client = speech.SpeechClient()
            except ImportError:
                raise ImportError(
                    "google-cloud-speech not installed. Run: pip install google-cloud-speech"
                )
            except Exception as e:
                raise Exception(f"Failed to initialize Google STT client: {e}")
        return self.client
    
    def call(self, input_data: Any, **kwargs) -> ToolResult:
        """
        Transcribe audio using Google Cloud STT.
        
        Args:
            input_data: Audio bytes (WAV/FLAC format) or text string (fallback)
            **kwargs: Additional parameters (language_code, etc.)
            
        Returns:
            ToolResult with transcript
        """
        try:
            # If input is already text (from Web Speech API), return it
            if isinstance(input_data, str):
                return ToolResult(
                    success=True,
                    output=input_data,
                    metadata={"source": "text_passthrough"}
                )
            
            # Otherwise, process audio bytes
            from google.cloud import speech
            
            client = self._get_client()
            
            # Configure audio
            audio = speech.RecognitionAudio(content=input_data)
            
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=kwargs.get('sample_rate', 16000),
                language_code=kwargs.get('language_code', 'en-US'),
                enable_automatic_punctuation=True,
                model='latest_long',  # Use latest model for best accuracy
                use_enhanced=True,  # Use enhanced model (SOTA)
            )
            
            # Perform recognition
            response = client.recognize(config=config, audio=audio)
            
            # Extract transcript
            if response.results:
                transcript = response.results[0].alternatives[0].transcript
                confidence = response.results[0].alternatives[0].confidence
                
                return ToolResult(
                    success=True,
                    output=transcript,
                    metadata={
                        "confidence": confidence,
                        "model": "google_stt_enhanced"
                    }
                )
            else:
                return ToolResult(
                    success=False,
                    output=None,
                    error="No speech detected in audio"
                )
            
        except Exception as e:
            # Fallback: if it's a string, just return it
            if isinstance(input_data, str):
                return ToolResult(
                    success=True,
                    output=input_data,
                    metadata={"source": "fallback"}
                )
            
            return ToolResult(
                success=False,
                output=None,
                error=f"Google STT error: {str(e)}"
            )


class GroqSTTTool(Tool):
    """Groq Whisper API wrapper."""
    
    def __init__(self):
        super().__init__(
            name="Groq Whisper",
            description="Groq Whisper Speech-to-Text API"
        )
    
    def call(self, input_data: Any, **kwargs) -> ToolResult:
        """
        Transcribe audio using Groq Whisper.
        
        Args:
            input_data: Audio file path or bytes
            
        Returns:
            ToolResult with transcript
        """
        try:
            # TODO: Implement real Groq Whisper API
            # from groq import Groq
            
            # For now, mock implementation
            transcript = "create a function to fetch weather data"
            
            return ToolResult(
                success=True,
                output=transcript,
                metadata={"duration": "2.5s"}
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                output=None,
                error=str(e)
            )


def create_stt_tool() -> Tool:
    """Factory function to create the appropriate STT tool based on config."""
    if settings.STT_PROVIDER == "groq":
        return GroqSTTTool()
    else:
        return GoogleSTTTool()