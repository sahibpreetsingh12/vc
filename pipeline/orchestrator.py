"""
Pipeline Orchestrator - coordinates the multi-agent workflow.

Implements the ReAct pattern: agents reason and act using tools.
"""

from typing import Dict, Any, Optional
from dataclasses import dataclass

from agents.speech_agent import SpeechAgent
from agents.security_agent import SecurityAgent
from agents.reasoning_agent import ReasoningAgent
from agents.coder_agent import CoderAgent
from agents.validator_agent import ValidatorAgent

from tools.stt_tool import create_stt_tool
from tools.sanitizer_tool import SanitizerTool
from tools.llm_tool import create_llm_tool

from utils.logger import get_logger, reset_logger


@dataclass
class PipelineResult:
    """Result of the complete pipeline execution."""
    success: bool
    stage: str  # Which stage completed (speech, security, reasoning, coding, validation)
    data: Any
    error: Optional[str] = None
    metadata: Dict[str, Any] = None


class VoiceCursorPipeline:
    """
    Main orchestrator for the Voice Cursor system.
    
    Coordinates the 5-agent workflow:
    1. Speech Agent → text
    2. Security Agent → sanitized command
    3. Reasoning Agent → execution plan
    4. Coder Agent → generated code
    5. Validator Agent → validated/applied code
    """
    
    def __init__(self):
        # Initialize agents
        self.speech_agent = SpeechAgent()
        self.security_agent = SecurityAgent()
        self.reasoning_agent = ReasoningAgent()
        self.coder_agent = CoderAgent()
        self.validator_agent = ValidatorAgent()
        
        # Initialize logger
        self.logger = get_logger()
        
        # Initialize and register tools
        self._setup_tools()
    
    def _setup_tools(self):
        """Set up tools for each agent."""
        # Speech agent gets STT tool
        stt_tool = create_stt_tool()
        self.speech_agent.add_tool(stt_tool)
        
        # Security agent gets sanitizer tool
        sanitizer = SanitizerTool()
        self.security_agent.add_tool(sanitizer)
        
        # Reasoning agent gets LLM tool (for planning)
        planning_llm = create_llm_tool()
        self.reasoning_agent.add_tool(planning_llm)
        
        # Coder agent gets LLM tool (for code generation)
        codegen_llm = create_llm_tool()
        self.coder_agent.add_tool(codegen_llm)
        
        # Validator agent (no tools for now, can add syntax checkers)
    
    def execute(self, audio_input: Any, context: Optional[Dict] = None) -> PipelineResult:
        """
        Execute the complete pipeline.
        
        Args:
            audio_input: Audio file path or mock text for demo
            context: Optional context (file path, existing code, etc.)
            
        Returns:
            PipelineResult with final status
        """
        if context is None:
            context = {}
        
        # Reset logger for new pipeline run
        reset_logger()
        self.logger = get_logger()
        
        # Log pipeline start
        self.logger.log_pipeline_start(str(audio_input)[:100])
        
        # Stage 1: Speech to Text
        print("🎤️  Stage 1: Speech Agent (STT)")
        speech_result = self.speech_agent.execute(audio_input, context)
        
        # Log Stage 1
        self.logger.log_agent_call(
            agent_name="Speech Agent",
            input_data=audio_input,
            output_data=speech_result.data,
            success=speech_result.success,
            error=speech_result.error,
            metadata=speech_result.metadata
        )
        
        if not speech_result.success:
            self.logger.log_pipeline_end(success=False, error=speech_result.error)
            return PipelineResult(
                success=False,
                stage="speech",
                data=None,
                error=speech_result.error
            )
        
        transcript = speech_result.data
        print(f"   ✓ Transcript: {transcript}")
        
        # Stage 2: Security validation
        print("\n🛡️  Stage 2: Security Agent (Sanitization)")
        security_result = self.security_agent.execute(transcript, context)
        
        # Log Stage 2
        self.logger.log_agent_call(
            agent_name="Security Agent",
            input_data=transcript,
            output_data=security_result.data,
            success=security_result.success,
            error=security_result.error,
            metadata=security_result.metadata
        )
        
        if not security_result.success:
            self.logger.log_pipeline_end(success=False, error=security_result.error)
            return PipelineResult(
                success=False,
                stage="security",
                data=None,
                error=security_result.error
            )
        
        sanitized_command = security_result.data
        print(f"   ✓ Command sanitized: {sanitized_command}")
        
        # Stage 3: Planning
        print("\n🧠 Stage 3: Reasoning Agent (Planning)")
        reasoning_result = self.reasoning_agent.execute(sanitized_command, context)
        
        # Log Stage 3
        self.logger.log_agent_call(
            agent_name="Reasoning Agent",
            input_data=sanitized_command,
            output_data=reasoning_result.data,
            success=reasoning_result.success,
            error=reasoning_result.error,
            metadata=reasoning_result.metadata
        )
        
        if not reasoning_result.success:
            self.logger.log_pipeline_end(success=False, error=reasoning_result.error)
            return PipelineResult(
                success=False,
                stage="reasoning",
                data=None,
                error=reasoning_result.error
            )
        
        plan = reasoning_result.data
        print(f"   ✓ Plan created ({plan['step_count']} steps):")
        for i, step in enumerate(plan['steps'], 1):
            print(f"      {i}. {step}")
        
        # Stage 4: Code Generation
        print("\n👨‍💻 Stage 4: Coder Agent (Code Generation)")
        coder_result = self.coder_agent.execute(plan, context)
        
        # Log Stage 4
        self.logger.log_agent_call(
            agent_name="Coder Agent",
            input_data=plan,
            output_data=coder_result.data,
            success=coder_result.success,
            error=coder_result.error,
            metadata=coder_result.metadata
        )
        
        if not coder_result.success:
            self.logger.log_pipeline_end(success=False, error=coder_result.error)
            return PipelineResult(
                success=False,
                stage="coding",
                data=None,
                error=coder_result.error
            )
        
        code_data = coder_result.data
        print(f"   ✓ Code generated ({len(code_data['code'])} chars)")
        
        # Stage 5: Validation
        print("\n✅ Stage 5: Validator Agent (Review & Apply)")
        validator_result = self.validator_agent.execute(code_data, context)
        
        # Log Stage 5
        self.logger.log_agent_call(
            agent_name="Validator Agent",
            input_data=code_data,
            output_data=validator_result.data,
            success=validator_result.success,
            error=validator_result.error,
            metadata=validator_result.metadata
        )
        
        if not validator_result.success:
            self.logger.log_pipeline_end(success=False, error=validator_result.error)
            return PipelineResult(
                success=False,
                stage="validation",
                data=None,
                error=validator_result.error
            )
        
        validation_data = validator_result.data
        print(f"   ✓ Status: {validation_data['status']}")
        
        # Log pipeline end
        self.logger.log_pipeline_end(success=True)
        
        # Print log file locations
        print(f"\n📝 Logs saved to:")
        print(f"   Text: {self.logger.get_log_file_path()}")
        print(f"   JSON: {self.logger.get_json_log_path()}")
        
        return PipelineResult(
            success=True,
            stage="complete",
            data=validation_data,
            metadata={
                "transcript": transcript,
                "plan": plan,
                "code": code_data,
                "log_file": self.logger.get_log_file_path(),
                "json_log": self.logger.get_json_log_path()
            }
        )
    
    def approve_and_apply(self, code: str, context: Optional[Dict] = None):
        """
        Approve pending code and apply it.
        
        Args:
            code: The code to apply
            context: Context with file path, etc.
        """
        return self.validator_agent.approve_and_apply(code, context)