#!/usr/bin/env python3
"""
Complete Voice-to-Code Pipeline

Full pipeline:
1. Speech Agent (captures your real voice with Google STT)
2. Security Agent (sanitizes the command)
3. Reasoning Agent (creates execution plan with Gemini)
4. Coder Agent (generates code with Gemini)
5. Saves to output_test/ folder
6. Maintains logs
"""

import speech_recognition as sr
from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax
from rich.prompt import Confirm
from pathlib import Path
from datetime import datetime
import re

# Import agents
from agents.speech_agent import SpeechAgent
from agents.security_agent import SecurityAgent
from agents.reasoning_agent import ReasoningAgent
from agents.coder_agent import CoderAgent
from agents.validator_agent import ValidatorAgent

# Import tools
from tools.stt_tool import create_stt_tool
from tools.sanitizer_tool import SanitizerTool
from tools.llm_tool import GeminiLLMTool

# Import logging
from utils.logger import get_logger, reset_logger

console = Console()

# Output directory
OUTPUT_DIR = Path("output_test")
OUTPUT_DIR.mkdir(exist_ok=True)


def listen_for_voice_command():
    """Listen to microphone and capture real speech."""
    console.print(Panel("[bold cyan]🎤 Voice Input - Speak Your Command[/bold cyan]"))
    
    recognizer = sr.Recognizer()
    
    console.print("\n[yellow]🎤 Get ready to speak...[/yellow]")
    console.print("[dim]Press Enter when ready to speak[/dim]")
    
    try:
        input()  # Wait for user to press Enter
        
        with sr.Microphone() as source:
            console.print("\n[dim]Adjusting for background noise...[/dim]")
            recognizer.adjust_for_ambient_noise(source, duration=1)
            
            # Better voice recognition settings
            recognizer.energy_threshold = 300
            recognizer.dynamic_energy_threshold = True
            recognizer.pause_threshold = 1.5
            
            console.print("[bold green]🔴 Recording... Speak now![/bold green]")
            console.print("[dim](Will stop after 1.5 seconds of silence)[/dim]\n")
            
            # Listen with longer timeout
            audio = recognizer.listen(
                source, 
                timeout=10,  # Wait 10s for speech to start
                phrase_time_limit=30  # Allow 30s of continuous speech
            )
            
            console.print("[dim]Processing audio...[/dim]")
            
            # Transcribe using Google Speech Recognition
            text = recognizer.recognize_google(audio)
            
            console.print(f"\n[green]✓ Heard:[/green] \"{text}\"\n")
            return text
            
    except sr.WaitTimeoutError:
        console.print("[yellow]⏱️  No speech detected. Please try again.[/yellow]")
        return None
    except sr.UnknownValueError:
        console.print("[red]❌ Could not understand audio. Please try again.[/red]")
        return None
    except sr.RequestError as e:
        console.print(f"[red]❌ Speech recognition error: {e}[/red]")
        console.print("[yellow]Tip: Make sure you have internet connection[/yellow]")
        return None
    except Exception as e:
        console.print(f"[red]❌ Error: {str(e)}[/red]")
        return None


def test_speech_agent(voice_input):
    """Test Speech Agent with real voice input."""
    console.print(Panel("[bold cyan]🎤 Processing Speech with Google STT[/bold cyan]"))
    
    try:
        # Create agent
        agent = SpeechAgent()
        agent.add_tool(create_stt_tool())
        
        # Process the voice input
        result = agent.execute(voice_input)
        
        if result.success:
            console.print(f"[green]✅ Speech processed successfully![/green]")
            console.print(f"[green]Transcript:[/green] {result.data}")
            return result.data, result
        else:
            console.print(f"[red]❌ Speech processing failed:[/red] {result.error}")
            return None, None
            
    except Exception as e:
        console.print(f"[red]❌ Exception:[/red] {str(e)}")
        return None, None


def test_security_agent(transcript):
    """Test Security Agent with the transcript."""
    console.print(Panel("[bold cyan]🛡️ Security Validation[/bold cyan]"))
    
    try:
        # Create agent
        agent = SecurityAgent()
        agent.add_tool(SanitizerTool())
        
        # Sanitize the command
        result = agent.execute(transcript)
        
        if result.success:
            console.print(f"[green]✅ Command is safe![/green]")
            console.print(f"[green]Sanitized:[/green] {result.data}")
            return result.data, result
        else:
            console.print(f"[red]❌ Command rejected:[/red] {result.error}")
            return None, None
            
    except Exception as e:
        console.print(f"[red]❌ Exception:[/red] {str(e)}")
        return None, None


def test_reasoning_agent(sanitized_command):
    """Test Reasoning Agent with Gemini."""
    console.print(Panel("[bold cyan]🧠 Planning with Gemini 2.0 Flash[/bold cyan]"))
    
    try:
        # Create agent
        agent = ReasoningAgent()
        agent.add_tool(GeminiLLMTool())
        
        console.print(f"[yellow]Creating plan for:[/yellow] {sanitized_command}")
        
        result = agent.execute(sanitized_command)
        
        if result.success:
            console.print(f"[green]✅ Plan created successfully![/green]")
            console.print(f"[green]Execution Plan ({result.data['step_count']} steps):[/green]")
            for i, step in enumerate(result.data['steps'], 1):
                console.print(f"  {i}. {step}")
            return result.data, result
        else:
            console.print(f"[red]❌ Planning failed:[/red] {result.error}")
            return None, None
            
    except Exception as e:
        console.print(f"[red]❌ Exception:[/red] {str(e)}")
        import traceback
        traceback.print_exc()
        return None, None


def test_coder_agent(plan_data):
    """Test Coder Agent with Gemini."""
    console.print(Panel("[bold cyan]👨‍💻 Generating Code with Gemini 2.0 Flash[/bold cyan]"))
    
    try:
        # Create agent
        agent = CoderAgent()
        agent.add_tool(GeminiLLMTool())
        
        console.print(f"[yellow]Generating code for:[/yellow] {plan_data['command']}")
        console.print(f"[yellow]Using {len(plan_data['steps'])} steps from planner[/yellow]")
        
        result = agent.execute(plan_data, context={'language': 'python'})
        
        if result.success:
            code = result.data['code']
            console.print(f"[green]✅ Code generated successfully![/green]")
            console.print(f"[green]Generated {len(code)} characters of Python code[/green]")
            
            # Show code with syntax highlighting
            console.print(f"\n[bold green]Generated Code:[/bold green]")
            syntax = Syntax(code, "python", theme="monokai", line_numbers=True)
            console.print(syntax)
            
            return result.data, result
        else:
            console.print(f"[red]❌ Code generation failed:[/red] {result.error}")
            return None, None
            
    except Exception as e:
        console.print(f"[red]❌ Exception:[/red] {str(e)}")
        import traceback
        traceback.print_exc()
        return None, None


def generate_filename(command: str, language: str = "python") -> str:
    """Generate a filename based on the command."""
    # Extract key words from command
    command_lower = command.lower()
    
    # Try to extract a meaningful name
    if "function" in command_lower:
        # Extract function name if mentioned
        words = command_lower.replace("function", "").replace("to", "").split()
        name = "_".join([w for w in words[:3] if len(w) > 2])
    elif "class" in command_lower:
        words = command_lower.replace("class", "").replace("to", "").split()
        name = "_".join([w for w in words[:3] if len(w) > 2])
    elif "api" in command_lower or "endpoint" in command_lower:
        words = command_lower.replace("api", "").replace("endpoint", "").split()
        name = "api_" + "_".join([w for w in words[:2] if len(w) > 2])
    else:
        # Use first few words
        words = [w for w in command_lower.split() if len(w) > 2][:3]
        name = "_".join(words) if words else "generated"
    
    # Clean up the name
    name = re.sub(r'[^a-z0-9_]', '', name.replace(' ', '_'))
    name = name[:30]  # Limit length
    
    # Add timestamp to make it unique
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
    
    # Determine extension
    ext = {"python": "py", "javascript": "js", "typescript": "ts"}.get(language, "txt")
    
    return f"{name}_{timestamp}.{ext}"


def save_code_to_file(code: str, command: str) -> str:
    """Save generated code to output_test folder."""
    filename = generate_filename(command)
    filepath = OUTPUT_DIR / filename
    
    try:
        with open(filepath, 'w') as f:
            f.write(code)
        return str(filepath)
    except Exception as e:
        console.print(f"[red]❌ Failed to save file: {e}[/red]")
        return None


def main():
    """Main voice-to-code pipeline function."""
    console.print("\n[bold cyan]🎙️ Voice-to-Code Pipeline[/bold cyan]\n")
    console.print("[dim]Speak your command → AI generates code → Saves to file + logs[/dim]\n")
    
    # Initialize logging
    reset_logger()
    logger = get_logger()
    
    try:
        # Step 1: Listen for voice input
        console.print("="*70)
        voice_input = listen_for_voice_command()
        
        if not voice_input:
            console.print("[red]❌ No valid voice input received. Exiting.[/red]")
            return
        
        # Log pipeline start
        logger.log_pipeline_start(voice_input)
        
        # Step 2: Process speech with Speech Agent
        console.print("\n" + "="*70)
        transcript, speech_result = test_speech_agent(voice_input)
        
        if not transcript:
            logger.log_pipeline_end(success=False, error="Speech processing failed")
            return
        
        # Log Speech Agent
        logger.log_agent_call(
            agent_name="Speech Agent",
            input_data=voice_input,
            output_data=transcript,
            success=True,
            metadata=speech_result.metadata if speech_result else {}
        )
        
        # Step 3: Sanitize with Security Agent
        console.print("\n" + "="*70)
        sanitized_command, security_result = test_security_agent(transcript)
        
        if not sanitized_command:
            logger.log_pipeline_end(success=False, error="Security validation failed")
            return
        
        # Log Security Agent
        logger.log_agent_call(
            agent_name="Security Agent",
            input_data=transcript,
            output_data=sanitized_command,
            success=True,
            metadata=security_result.metadata if security_result else {}
        )
        
        # Step 4: Plan with Reasoning Agent
        console.print("\n" + "="*70)
        plan_data, reasoning_result = test_reasoning_agent(sanitized_command)
        
        if not plan_data:
            logger.log_pipeline_end(success=False, error="Planning failed")
            return
        
        # Log Reasoning Agent
        logger.log_agent_call(
            agent_name="Reasoning Agent",
            input_data=sanitized_command,
            output_data=plan_data,
            success=True,
            metadata=reasoning_result.metadata if reasoning_result else {}
        )
        
        # Step 5: Generate code with Coder Agent
        console.print("\n" + "="*70)
        code_data, coder_result = test_coder_agent(plan_data)
        
        if not code_data:
            logger.log_pipeline_end(success=False, error="Code generation failed")
            return
        
        # Log Coder Agent
        logger.log_agent_call(
            agent_name="Coder Agent",
            input_data=plan_data,
            output_data=code_data,
            success=True,
            metadata=coder_result.metadata if coder_result else {}
        )
        
        # Step 6: Save to file
        console.print("\n" + "="*70)
        console.print(Panel("[bold cyan]💾 Saving Generated Code[/bold cyan]"))
        
        code = code_data['code']
        command = plan_data['command']
        
        filepath = save_code_to_file(code, command)
        
        if filepath:
            console.print(f"[green]✅ Code saved successfully![/green]")
            console.print(f"[green]File:[/green] {filepath}")
            console.print(f"[green]Size:[/green] {len(code)} characters")
        
        # Log completion
        logger.log_pipeline_end(success=True)
        
        # Final Summary
        console.print("\n" + "="*70)
        console.print(Panel("[bold]🎉 Pipeline Complete![/bold]"))
        
        console.print(f"\n[bold]Summary:[/bold]")
        console.print(f"  🎤 Voice Input: {voice_input}")
        console.print(f"  🛡️  Sanitized: {sanitized_command}")
        console.print(f"  🧠 Plan Steps: {len(plan_data['steps'])}")
        console.print(f"  👨‍💻 Code Generated: {len(code)} chars")
        console.print(f"  💾 Saved to: {filepath}")
        
        # Log file locations
        console.print(f"\n[bold]📝 Logs:[/bold]")
        console.print(f"  Text: {logger.get_log_file_path()}")
        console.print(f"  JSON: {logger.get_json_log_path()}")
        
        console.print(f"\n[green]✨ Success! Your voice command has been turned into code![/green]\n")
        
    except KeyboardInterrupt:
        console.print("\n\n[yellow]❌ Interrupted by user[/yellow]")
        logger.log_pipeline_end(success=False, error="Interrupted by user")
    except Exception as e:
        console.print(f"\n[red]❌ Pipeline error: {str(e)}[/red]")
        logger.log_pipeline_end(success=False, error=str(e))
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()