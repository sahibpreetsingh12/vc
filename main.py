#!/usr/bin/env python3
"""
Voice Cursor - Multi-Agent Voice IDE

Main entry point for the system.
"""

from rich.console import Console
from rich.panel import Panel
from rich.syntax import Syntax

from pipeline import VoiceCursorPipeline
from config import settings


console = Console()


def print_header():
    """Print welcome header."""
    console.print(Panel.fit(
        "[bold cyan]🎙️ Voice Cursor[/bold cyan]\n"
        "[dim]Multi-Agent Voice IDE for Google Hackathon[/dim]",
        border_style="cyan"
    ))


def print_code_result(code: str, language: str = "python"):
    """Pretty print generated code."""
    syntax = Syntax(code, language, theme="monokai", line_numbers=True)
    console.print("\n[bold green]Generated Code:[/bold green]")
    console.print(syntax)


def demo_mode():
    """
    Run a demo of the system with mock voice input.
    """
    print_header()
    
    console.print("\n[yellow]Running in DEMO mode with mock voice input[/yellow]")
    console.print("[dim]In production, this would use real audio input[/dim]\n")
    
    # Initialize pipeline
    pipeline = VoiceCursorPipeline()
    
    # Mock audio input (in real system, this would be actual audio)
    mock_voice_command = "create a function to fetch weather data"
    
    console.print(f"[bold]Voice Command:[/bold] \"{mock_voice_command}\"\n")
    
    # Execute pipeline
    result = pipeline.execute(
        audio_input=mock_voice_command,
        context={
            "language": "python",
            "require_approval": True
        }
    )
    
    # Display results
    if result.success:
        console.print("\n[bold green]✓ Pipeline completed successfully![/bold green]\n")
        
        # Show generated code
        if "code" in result.data:
            code = result.data["code"]
            print_code_result(code)
            
            # Show approval prompt
            console.print("\n[yellow]⚠️  Code requires approval before applying[/yellow]")
            console.print("[dim]Status: pending_approval[/dim]")
            console.print("\n[bold]Next steps:[/bold]")
            console.print("  1. Review the generated code")
            console.print("  2. Call approve_and_apply() to write to file")
    else:
        console.print(f"\n[bold red]✗ Pipeline failed at stage: {result.stage}[/bold red]")
        console.print(f"[red]Error: {result.error}[/red]")


def interactive_mode():
    """
    Interactive mode (future implementation).
    
    Would include:
    - Real microphone input
    - Continuous listening
    - File browser integration
    """
    console.print("[yellow]Interactive mode not yet implemented[/yellow]")
    console.print("Use demo_mode() for now")


def main():
    """Main entry point."""
    import sys
    
    if len(sys.argv) > 1 and sys.argv[1] == "--interactive":
        interactive_mode()
    else:
        demo_mode()


if __name__ == "__main__":
    main()