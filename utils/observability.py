"""
Observability module for tracking agent pipeline metrics.

Tracks:
- Agents used
- Query/command
- Tools used and their order
- Token count per tool/agent
- Cost calculation
- Step-wise latency
"""

import json
import time
from datetime import datetime
from pathlib import Path
from typing import Any, Dict, List, Optional
from dataclasses import dataclass, asdict


@dataclass
class ToolUsage:
    """Track individual tool usage."""
    name: str
    order: int
    input_length: int
    output_length: int
    tokens: int
    latency_ms: float
    timestamp: str


@dataclass
class AgentExecution:
    """Track individual agent execution."""
    name: str
    stage: str
    tools_used: List[str]
    tokens: int
    latency_ms: float
    success: bool
    timestamp: str


@dataclass
class ObservabilityRecord:
    """Complete observability record for a single request."""
    id: str
    query: str
    timestamp: str
    agents: List[AgentExecution]
    tools: List[ToolUsage]
    total_tokens: int
    total_cost_usd: float
    total_latency_ms: float
    success: bool
    error: Optional[str] = None


class ObservabilityTracker:
    """Track observability metrics for agent pipeline execution."""
    
    # Pricing per 1M tokens (update these based on your provider pricing)
    PRICING = {
        "gemini-2.0-flash-exp": {
            "input": 0.00,  # Free tier
            "output": 0.00  # Free tier
        },
        "llama-3.3-70b-versatile": {
            "input": 0.59,  # $0.59 per 1M tokens
            "output": 0.79  # $0.79 per 1M tokens
        },
        "google_stt_enhanced": {
            "per_minute": 0.009  # $0.009 per minute
        },
        "web_speech_api": {
            "per_minute": 0.00  # Free
        }
    }
    
    def __init__(self, storage_path: str = "logs/observability"):
        """Initialize tracker with storage path."""
        self.storage_path = Path(storage_path)
        self.storage_path.mkdir(parents=True, exist_ok=True)
        
        # Current tracking state
        self.current_record: Optional[Dict] = None
        self.records: List[ObservabilityRecord] = []
        
        # Load existing records
        self._load_records()
    
    def start_tracking(self, query: str) -> str:
        """Start tracking a new request."""
        record_id = f"{datetime.now().strftime('%Y%m%d_%H%M%S_%f')}"
        
        self.current_record = {
            "id": record_id,
            "query": query,
            "timestamp": datetime.now().isoformat(),
            "start_time": time.time(),
            "agents": [],
            "tools": [],
            "total_tokens": 0,
            "total_cost_usd": 0.0,
            "success": False,
            "error": None
        }
        
        return record_id
    
    def track_agent_start(self, agent_name: str, stage: str):
        """Track the start of an agent execution."""
        if not self.current_record:
            return
        
        self.current_record[f"agent_{stage}_start"] = time.time()
        self.current_record[f"agent_{stage}_name"] = agent_name
    
    def track_agent_end(self, agent_name: str, stage: str, tools_used: List[str], 
                        tokens: int = 0, success: bool = True):
        """Track the end of an agent execution."""
        if not self.current_record:
            return
        
        start_key = f"agent_{stage}_start"
        if start_key not in self.current_record:
            return
        
        latency = (time.time() - self.current_record[start_key]) * 1000  # Convert to ms
        
        agent_exec = AgentExecution(
            name=agent_name,
            stage=stage,
            tools_used=tools_used,
            tokens=tokens,
            latency_ms=round(latency, 2),
            success=success,
            timestamp=datetime.now().isoformat()
        )
        
        self.current_record["agents"].append(agent_exec)
        self.current_record["total_tokens"] += tokens
    
    def track_tool_usage(self, tool_name: str, input_data: Any, output_data: Any,
                         tokens: int = 0, latency_ms: float = 0):
        """Track individual tool usage."""
        if not self.current_record:
            return
        
        order = len(self.current_record["tools"]) + 1
        
        input_length = len(str(input_data)) if input_data else 0
        output_length = len(str(output_data)) if output_data else 0
        
        tool_usage = ToolUsage(
            name=tool_name,
            order=order,
            input_length=input_length,
            output_length=output_length,
            tokens=tokens,
            latency_ms=round(latency_ms, 2),
            timestamp=datetime.now().isoformat()
        )
        
        self.current_record["tools"].append(tool_usage)
        
        # Calculate cost for this tool
        cost = self._calculate_tool_cost(tool_name, tokens, input_length, output_length)
        self.current_record["total_cost_usd"] += cost
    
    def _calculate_tool_cost(self, tool_name: str, tokens: int, 
                            input_length: int, output_length: int) -> float:
        """Calculate cost for a tool usage."""
        # Estimate token counts (rough approximation: 1 token ≈ 4 characters)
        estimated_input_tokens = input_length / 4
        estimated_output_tokens = output_length / 4
        
        # Use provided tokens if available, otherwise use estimates
        if tokens > 0:
            total_tokens = tokens
        else:
            total_tokens = estimated_input_tokens + estimated_output_tokens
        
        # Find pricing
        for model_key, pricing in self.PRICING.items():
            if model_key.lower() in tool_name.lower():
                if "per_minute" in pricing:
                    # For STT - estimate duration (rough: 150 words per minute)
                    estimated_minutes = max(input_length / 150 / 60, 0.1)
                    return pricing["per_minute"] * estimated_minutes
                else:
                    # For LLM - calculate based on tokens
                    input_cost = (estimated_input_tokens / 1_000_000) * pricing.get("input", 0)
                    output_cost = (estimated_output_tokens / 1_000_000) * pricing.get("output", 0)
                    return input_cost + output_cost
        
        return 0.0  # Default if pricing not found
    
    def end_tracking(self, success: bool = True, error: Optional[str] = None):
        """End tracking and save the record."""
        if not self.current_record:
            return
        
        total_latency = (time.time() - self.current_record["start_time"]) * 1000
        
        record = ObservabilityRecord(
            id=self.current_record["id"],
            query=self.current_record["query"],
            timestamp=self.current_record["timestamp"],
            agents=self.current_record["agents"],
            tools=self.current_record["tools"],
            total_tokens=self.current_record["total_tokens"],
            total_cost_usd=round(self.current_record["total_cost_usd"], 6),
            total_latency_ms=round(total_latency, 2),
            success=success,
            error=error
        )
        
        self.records.append(record)
        self._save_record(record)
        
        # Reset current tracking
        self.current_record = None
    
    def _save_record(self, record: ObservabilityRecord):
        """Save a single record to disk."""
        file_path = self.storage_path / f"{record.id}.json"
        
        with open(file_path, 'w', encoding='utf-8') as f:
            json.dump(asdict(record), f, indent=2, ensure_ascii=False)
    
    def _load_records(self):
        """Load all existing records from disk."""
        if not self.storage_path.exists():
            return
        
        json_files = sorted(self.storage_path.glob("*.json"), reverse=True)
        
        # Load up to last 100 records
        for json_file in json_files[:100]:
            try:
                with open(json_file, 'r', encoding='utf-8') as f:
                    data = json.load(f)
                    
                    # Reconstruct dataclass objects
                    agents = [AgentExecution(**a) for a in data.get("agents", [])]
                    tools = [ToolUsage(**t) for t in data.get("tools", [])]
                    
                    record = ObservabilityRecord(
                        id=data["id"],
                        query=data["query"],
                        timestamp=data["timestamp"],
                        agents=agents,
                        tools=tools,
                        total_tokens=data["total_tokens"],
                        total_cost_usd=data["total_cost_usd"],
                        total_latency_ms=data["total_latency_ms"],
                        success=data["success"],
                        error=data.get("error")
                    )
                    
                    self.records.append(record)
            except Exception as e:
                print(f"Error loading record {json_file}: {e}")
    
    def get_all_records(self) -> List[Dict]:
        """Get all records as dictionaries."""
        return [asdict(record) for record in self.records]
    
    def get_summary_stats(self) -> Dict:
        """Get summary statistics across all records."""
        if not self.records:
            return {
                "total_requests": 0,
                "successful_requests": 0,
                "failed_requests": 0,
                "total_tokens": 0,
                "total_cost_usd": 0.0,
                "avg_latency_ms": 0.0,
                "total_agents_used": 0,
                "total_tools_used": 0
            }
        
        total_requests = len(self.records)
        successful = sum(1 for r in self.records if r.success)
        failed = total_requests - successful
        total_tokens = sum(r.total_tokens for r in self.records)
        total_cost = sum(r.total_cost_usd for r in self.records)
        avg_latency = sum(r.total_latency_ms for r in self.records) / total_requests
        
        # Count unique agents and tools
        all_agents = set()
        all_tools = set()
        for record in self.records:
            for agent in record.agents:
                all_agents.add(agent.name)
            for tool in record.tools:
                all_tools.add(tool.name)
        
        return {
            "total_requests": total_requests,
            "successful_requests": successful,
            "failed_requests": failed,
            "total_tokens": total_tokens,
            "total_cost_usd": round(total_cost, 6),
            "avg_latency_ms": round(avg_latency, 2),
            "total_agents_used": len(all_agents),
            "total_tools_used": len(all_tools)
        }


# Global tracker instance
_global_tracker: Optional[ObservabilityTracker] = None


def get_tracker() -> ObservabilityTracker:
    """Get or create the global observability tracker."""
    global _global_tracker
    if _global_tracker is None:
        _global_tracker = ObservabilityTracker()
    return _global_tracker


def reset_tracker():
    """Reset the global tracker."""
    global _global_tracker
    _global_tracker = ObservabilityTracker()
