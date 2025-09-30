#!/usr/bin/env python3
"""
Log Viewer - View agent call logs

Shows the most recent log file or a specific log.
"""

import json
import sys
from pathlib import Path
from rich.console import Console
from rich.table import Table
from rich.panel import Panel
from rich.syntax import Syntax

console = Console()


def list_logs():
    """List all available log files."""
    log_dir = Path("logs")
    if not log_dir.exists():
        console.print("[yellow]No logs directory found[/yellow]")
        return []
    
    log_files = sorted(log_dir.glob("agent_calls_*.log"), reverse=True)
    return log_files


def view_text_log(log_file: Path):
    """View a text log file."""
    console.print(Panel(f"[bold cyan]Log File: {log_file.name}[/bold cyan]"))
    
    with open(log_file, 'r', encoding='utf-8') as f:
        content = f.read()
    
    console.print(content)


def view_json_log(json_file: Path):
    """View a JSON log file with formatted output."""
    with open(json_file, 'r', encoding='utf-8') as f:
        logs = json.load(f)
    
    console.print(Panel(f"[bold cyan]JSON Log: {json_file.name}[/bold cyan]"))
    console.print(f"[dim]Total entries: {len(logs)}[/dim]\n")
    
    for i, entry in enumerate(logs, 1):
        if "agent" in entry:
            # Agent call
            console.print(f"\n[bold]{'='*60}[/bold]")
            console.print(f"[bold cyan]Agent #{i}: {entry['agent']}[/bold cyan]")
            console.print(f"[dim]Time: {entry['timestamp']}[/dim]")
            console.print(f"Success: {'✅' if entry['success'] else '❌'}")
            
            if entry['error']:
                console.print(f"[red]Error: {entry['error']}[/red]")
            
            console.print(f"\n[yellow]Input:[/yellow]")
            console.print(json.dumps(entry['input'], indent=2)[:500])
            
            console.print(f"\n[green]Output:[/green]")
            console.print(json.dumps(entry['output'], indent=2)[:500])
            
            if entry.get('metadata'):
                console.print(f"\n[blue]Metadata:[/blue]")
                console.print(json.dumps(entry['metadata'], indent=2))
        
        elif "tool" in entry:
            # Tool call
            console.print(f"\n[dim]Tool: {entry['tool']} - {'✅' if entry['success'] else '❌'}[/dim]")


def view_summary(json_file: Path):
    """Show a summary table of agent calls."""
    with open(json_file, 'r', encoding='utf-8') as f:
        logs = json.load(f)
    
    # Filter agent calls
    agent_calls = [log for log in logs if "agent" in log]
    
    if not agent_calls:
        console.print("[yellow]No agent calls found in log[/yellow]")
        return
    
    # Create table
    table = Table(title=f"Agent Call Summary - {json_file.name}")
    table.add_column("#", style="cyan")
    table.add_column("Agent", style="bold")
    table.add_column("Status", style="green")
    table.add_column("Time", style="dim")
    table.add_column("Input (preview)", style="yellow")
    table.add_column("Error", style="red")
    
    for i, call in enumerate(agent_calls, 1):
        status = "✅" if call['success'] else "❌"
        time = call['timestamp'].split('T')[1].split('.')[0]  # Extract HH:MM:SS
        input_preview = str(call['input'])[:50] + "..." if len(str(call['input'])) > 50 else str(call['input'])
        error = call['error'] if call['error'] else ""
        
        table.add_row(
            str(i),
            call['agent'],
            status,
            time,
            input_preview,
            error[:50] if error else ""
        )
    
    console.print(table)


def main():
    """Main function."""
    console.print("\n[bold cyan]📝 Voice Cursor Log Viewer[/bold cyan]\n")
    
    # List available logs
    log_files = list_logs()
    
    if not log_files:
        console.print("[yellow]No log files found. Run voice_interactive.py first![/yellow]")
        return
    
    console.print(f"[green]Found {len(log_files)} log file(s)[/green]\n")
    
    # Check for command line arguments
    if len(sys.argv) > 1:
        command = sys.argv[1]
        
        if command == "list":
            for i, log in enumerate(log_files, 1):
                console.print(f"{i}. {log.name}")
            return
        
        elif command == "summary":
            # Show summary of latest
            json_file = Path(str(log_files[0]).replace('.log', '.json'))
            if json_file.exists():
                view_summary(json_file)
            else:
                console.print("[red]JSON log not found[/red]")
            return
        
        elif command == "json":
            # Show JSON of latest
            json_file = Path(str(log_files[0]).replace('.log', '.json'))
            if json_file.exists():
                view_json_log(json_file)
            else:
                console.print("[red]JSON log not found[/red]")
            return
    
    # Default: show text log of latest
    latest = log_files[0]
    console.print(f"[bold]Showing latest log:[/bold] {latest.name}\n")
    view_text_log(latest)
    
    console.print(f"\n[dim]Tip: Use 'python view_logs.py summary' for a quick overview[/dim]")
    console.print(f"[dim]Tip: Use 'python view_logs.py json' for detailed JSON view[/dim]")
    console.print(f"[dim]Tip: Use 'python view_logs.py list' to list all logs[/dim]")


if __name__ == "__main__":
    main()