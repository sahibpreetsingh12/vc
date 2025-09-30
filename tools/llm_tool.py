"""
LLM Tool - wraps various LLM providers (Gemini, Groq, etc).
"""

from typing import Any
from .base import Tool, ToolResult
from config import settings


class GeminiLLMTool(Tool):
    """Google Gemini LLM wrapper - Real API implementation."""
    
    def __init__(self, model: str = "gemini-2.0-flash-exp"):
        super().__init__(
            name="Gemini 2.0 Flash",
            description="Google Gemini 2.0 Flash (Experimental)"
        )
        self.model = model
        self.client = None
    
    def _get_client(self):
        """Lazy initialization of Gemini client."""
        if self.client is None:
            try:
                import google.generativeai as genai
                # Configure Gemini with API key from settings
                genai.configure(api_key=settings.GEMINI_API_KEY)
                self.client = genai.GenerativeModel(self.model)
            except ImportError:
                raise ImportError("google-generativeai package not installed. Run: pip install google-generativeai")
            except Exception as e:
                raise Exception(f"Failed to initialize Gemini client: {e}")
        return self.client
    
    def call(self, input_data: Any, **kwargs) -> ToolResult:
        """
        Generate text using Gemini API.
        
        Args:
            input_data: Text prompt
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
            
        Returns:
            ToolResult with generated text
        """
        try:
            prompt = str(input_data)
            
            # Get Gemini client
            model = self._get_client()
            
            # Configure generation
            generation_config = {
                "temperature": kwargs.get("temperature", 0.7),
                "max_output_tokens": kwargs.get("max_tokens", 2048),
            }
            
            # Call Gemini API
            response = model.generate_content(
                prompt,
                generation_config=generation_config
            )
            
            # Extract text
            output = response.text
            
            return ToolResult(
                success=True,
                output=output,
                metadata={
                    "model": self.model,
                    "tokens": len(output.split())  # Approximate token count
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                output=None,
                error=f"Gemini API error: {str(e)}"
            )


class GroqLLMTool(Tool):
    """Groq LLM wrapper - Real API implementation."""
    
    def __init__(self, model: str = "llama-3.3-70b-versatile"):
        super().__init__(
            name="Groq LLM",
            description="Groq language model"
        )
        self.model = model
        self.client = None
    
    def _get_client(self):
        """Lazy initialization of Groq client."""
        if self.client is None:
            try:
                from groq import Groq
                import os
                # Set API key via environment variable (more reliable)
                os.environ['GROQ_API_KEY'] = settings.GROQ_API_KEY
                self.client = Groq()
            except ImportError:
                raise ImportError("groq package not installed. Run: pip install groq")
            except Exception as e:
                raise Exception(f"Failed to initialize Groq client: {e}")
        return self.client
    
    def call(self, input_data: Any, **kwargs) -> ToolResult:
        """
        Generate text using Groq API.
        
        Args:
            input_data: Text prompt
            **kwargs: Additional parameters (temperature, max_tokens, etc.)
            
        Returns:
            ToolResult with generated text
        """
        try:
            prompt = str(input_data)
            
            # Get Groq client
            client = self._get_client()
            
            # Call Groq API
            completion = client.chat.completions.create(
                model=self.model,
                messages=[
                    {
                        "role": "system",
                        "content": "You are an expert programmer. Generate clear, working code based on user requests. Be concise and practical."
                    },
                    {
                        "role": "user",
                        "content": prompt
                    }
                ],
                temperature=kwargs.get("temperature", 0.7),
                max_tokens=kwargs.get("max_tokens", 2048),
            )
            
            response = completion.choices[0].message.content
            
            return ToolResult(
                success=True,
                output=response,
                metadata={
                    "model": self.model,
                    "tokens": completion.usage.total_tokens if hasattr(completion, 'usage') else 0
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                output=None,
                error=f"Groq API error: {str(e)}"
            )


def create_llm_tool() -> Tool:
    """Factory function to create the appropriate LLM tool based on config."""
    if settings.LLM_PROVIDER == "groq":
        return GroqLLMTool()
    else:
        return GeminiLLMTool()