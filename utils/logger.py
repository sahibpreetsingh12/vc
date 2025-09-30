"""
Logging utility for Voice Cursor agents.

Logs each agent call with input, output, and timing information.
"""

import json
import logging
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, Optional


class AgentLogger:
    """Logger for agent pipeline execution."""
    
    def __init__(self, log_dir: str = "logs"):
        """Initialize logger with log directory."""
        self.log_dir = Path(log_dir)
        self.log_dir.mkdir(exist_ok=True)
        
        # Create timestamped log file
        timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")
        self.log_file = self.log_dir / f"agent_calls_{timestamp}.log"
        self.json_log_file = self.log_dir / f"agent_calls_{timestamp}.json"
        
        # Setup file logger
        self.logger = logging.getLogger("VoiceCursor")
        self.logger.setLevel(logging.DEBUG)
        
        # File handler
        fh = logging.FileHandler(self.log_file, encoding='utf-8')
        fh.setLevel(logging.DEBUG)
        
        # Format
        formatter = logging.Formatter(
            '%(asctime)s - %(name)s - %(levelname)s - %(message)s',
            datefmt='%Y-%m-%d %H:%M:%S'
        )
        fh.setFormatter(formatter)
        
        self.logger.addHandler(fh)
        
        # JSON log storage
        self.json_logs = []
    
    def log_agent_call(
        self, 
        agent_name: str, 
        input_data: Any, 
        output_data: Any, 
        success: bool, 
        error: Optional[str] = None,
        metadata: Optional[Dict] = None
    ):
        """
        Log an agent call with all details.
        
        Args:
            agent_name: Name of the agent
            input_data: Input passed to the agent
            output_data: Output from the agent
            success: Whether the agent call succeeded
            error: Error message if failed
            metadata: Additional metadata
        """
        timestamp = datetime.now().isoformat()
        
        # Create log entry
        log_entry = {
            "timestamp": timestamp,
            "agent": agent_name,
            "success": success,
            "input": self._serialize(input_data),
            "output": self._serialize(output_data),
            "error": error,
            "metadata": metadata or {}
        }
        
        # Log to file
        self.logger.info(f"{'='*80}")
        self.logger.info(f"AGENT: {agent_name}")
        self.logger.info(f"SUCCESS: {success}")
        self.logger.info(f"INPUT: {self._format_for_log(input_data)}")
        self.logger.info(f"OUTPUT: {self._format_for_log(output_data)}")
        if error:
            self.logger.error(f"ERROR: {error}")
        if metadata:
            self.logger.info(f"METADATA: {json.dumps(metadata, indent=2)}")
        self.logger.info(f"{'='*80}\n")
        
        # Store in JSON
        self.json_logs.append(log_entry)
    
    def log_tool_call(
        self,
        tool_name: str,
        input_data: Any,
        output_data: Any,
        success: bool,
        error: Optional[str] = None
    ):
        """
        Log a tool call.
        
        Args:
            tool_name: Name of the tool
            input_data: Input to the tool
            output_data: Output from the tool
            success: Whether the tool call succeeded
            error: Error message if failed
        """
        timestamp = datetime.now().isoformat()
        
        log_entry = {
            "timestamp": timestamp,
            "tool": tool_name,
            "success": success,
            "input": self._serialize(input_data)[:500],  # Truncate long inputs
            "output": self._serialize(output_data)[:500],  # Truncate long outputs
            "error": error
        }
        
        self.logger.debug(f"TOOL: {tool_name} - SUCCESS: {success}")
        if error:
            self.logger.debug(f"TOOL ERROR: {error}")
        
        self.json_logs.append(log_entry)
    
    def save_json_log(self):
        """Save all logs to JSON file."""
        with open(self.json_log_file, 'w', encoding='utf-8') as f:
            json.dump(self.json_logs, f, indent=2, ensure_ascii=False)
        
        self.logger.info(f"JSON log saved to: {self.json_log_file}")
    
    def _serialize(self, data: Any) -> Any:
        """Serialize data for logging."""
        if isinstance(data, (str, int, float, bool, type(None))):
            return data
        elif isinstance(data, dict):
            return {k: self._serialize(v) for k, v in data.items()}
        elif isinstance(data, (list, tuple)):
            return [self._serialize(item) for item in data]
        else:
            return str(data)
    
    def _format_for_log(self, data: Any, max_length: int = 500) -> str:
        """Format data for readable logging."""
        serialized = self._serialize(data)
        if isinstance(serialized, str):
            if len(serialized) > max_length:
                return serialized[:max_length] + "... (truncated)"
            return serialized
        
        json_str = json.dumps(serialized, indent=2, ensure_ascii=False)
        if len(json_str) > max_length:
            return json_str[:max_length] + "... (truncated)"
        return json_str
    
    def log_pipeline_start(self, command: str):
        """Log the start of a pipeline execution."""
        self.logger.info(f"\n{'#'*80}")
        self.logger.info(f"PIPELINE START")
        self.logger.info(f"Command: {command}")
        self.logger.info(f"Timestamp: {datetime.now().isoformat()}")
        self.logger.info(f"{'#'*80}\n")
    
    def log_pipeline_end(self, success: bool, error: Optional[str] = None):
        """Log the end of a pipeline execution."""
        self.logger.info(f"\n{'#'*80}")
        self.logger.info(f"PIPELINE END")
        self.logger.info(f"Success: {success}")
        if error:
            self.logger.error(f"Error: {error}")
        self.logger.info(f"Timestamp: {datetime.now().isoformat()}")
        self.logger.info(f"{'#'*80}\n")
        
        # Save JSON log
        self.save_json_log()
    
    def get_log_file_path(self) -> str:
        """Get the path to the current log file."""
        return str(self.log_file.absolute())
    
    def get_json_log_path(self) -> str:
        """Get the path to the JSON log file."""
        return str(self.json_log_file.absolute())


# Global logger instance
_global_logger: Optional[AgentLogger] = None


def get_logger() -> AgentLogger:
    """Get or create the global logger instance."""
    global _global_logger
    if _global_logger is None:
        _global_logger = AgentLogger()
    return _global_logger


def reset_logger():
    """Reset the global logger (creates new log files)."""
    global _global_logger
    _global_logger = AgentLogger()