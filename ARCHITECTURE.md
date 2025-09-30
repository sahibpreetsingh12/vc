# 🏗️ Voice Cursor Architecture

**A deep dive into the design, patterns, and implementation of the Voice Cursor system**

---

## Table of Contents

- [Overview](#overview)
- [Design Principles](#design-principles)
- [Multi-Agent System](#multi-agent-system)
- [ReAct Pattern](#react-pattern)
- [Tool Abstraction Layer](#tool-abstraction-layer)
- [Gemini Integration](#gemini-integration)
- [Data Flow](#data-flow)
- [Component Details](#component-details)
- [Extensibility](#extensibility)

---

## Overview

Voice Cursor is built on a **multi-agent architecture** where specialized agents collaborate to transform voice input into production-ready code. Each agent has a single responsibility and communicates through standardized interfaces.

### Key Components

```
┌─────────────────────────────────────────────────────┐
│                  Voice Cursor System                │
├─────────────────────────────────────────────────────┤
│                                                     │
│  ┌─────────────┐      ┌──────────────┐           │
│  │   Agents    │◄────►│    Tools     │           │
│  │             │      │              │           │
│  │ • Speech    │      │ • STT API    │           │
│  │ • Security  │      │ • LLM API    │           │
│  │ • Reasoning │      │ • Sanitizer  │           │
│  │ • Coder     │      │ • Formatter  │           │
│  │ • Validator │      └──────────────┘           │
│  └─────────────┘                                   │
│         ▲                                          │
│         │                                          │
│  ┌──────┴──────┐      ┌──────────────┐           │
│  │ Orchestrator│      │   Utilities  │           │
│  │  Pipeline   │      │              │           │
│  └─────────────┘      │ • Logger     │           │
│                       │ • Tracker    │           │
│                       └──────────────┘           │
└─────────────────────────────────────────────────────┘
```

---

## Design Principles

### 1. **Separation of Concerns**
Each agent handles one specific task:
- Speech Agent → Audio transcription
- Security Agent → Input validation
- Reasoning Agent → Planning
- Coder Agent → Code generation
- Validator Agent → Quality assurance

### 2. **Modularity**
- **Agents** are independent and can be replaced
- **Tools** are pluggable (swap Google STT for Whisper)
- **Pipeline** orchestrates without coupling

### 3. **Observability**
- Every agent call is logged
- Structured JSON logs for analysis
- Performance metrics tracked

### 4. **Extensibility**
- Add new agents without modifying existing code
- Plugin architecture for tools
- Clean base classes for inheritance

### 5. **Error Handling**
- Graceful degradation at each stage
- Detailed error context
- Recovery mechanisms

---

## Multi-Agent System

### Agent Base Class

All agents inherit from `Agent` base class:

```python
class Agent(ABC):
    """
    Base Agent following ReAct paradigm.
    
    Agents reason about inputs and act using tools.
    """
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
        self.tools = []
    
    def add_tool(self, tool):
        """Register a tool for this agent."""
        self.tools.append(tool)
    
    @abstractmethod
    def execute(self, input_data, context=None) -> AgentResult:
        """
        Execute agent logic.
        
        Args:
            input_data: Input specific to this agent
            context: Shared state between agents
            
        Returns:
            AgentResult with success, data, error
        """
        pass
```

### AgentResult Protocol

Standardized return format for all agents:

```python
@dataclass
class AgentResult:
    success: bool              # Did execution succeed?
    data: Any                  # Output data (varies by agent)
    error: Optional[str]       # Error message if failed
    metadata: Dict[str, Any]   # Additional info (timing, model, etc)
    timestamp: datetime        # When executed
```

### Agent Communication

Agents communicate through the **Pipeline Orchestrator**:

1. **Sequential execution**: Agents run in order
2. **Context passing**: Output of Agent N → Input of Agent N+1
3. **Early termination**: If any agent fails, pipeline stops
4. **Metadata accumulation**: Each agent adds metadata for observability

---

## ReAct Pattern

Voice Cursor implements the **ReAct (Reasoning + Acting)** pattern:

### Traditional Approach
```
Input → LLM → Output
```

### ReAct Approach
```
Input → Agent (Reason) → Tool (Act) → Agent (Process) → Output
```

### How We Use ReAct

#### Example: Reasoning Agent

```python
def execute(self, input_data, context):
    # 1. REASON: What tools do I need?
    if not self.tools:
        return AgentResult(success=False, error="No LLM tool")
    
    # 2. REASON: What prompt should I construct?
    prompt = self._create_planning_prompt(input_data)
    
    # 3. ACT: Call the LLM tool
    llm_tool = self.tools[0]
    result = llm_tool.call(prompt)
    
    # 4. REASON: Process the output
    plan = self._parse_plan(result.output)
    
    # 5. Return structured result
    return AgentResult(success=True, data=plan)
```

### Benefits

- **Modular reasoning**: Logic separated from execution
- **Tool flexibility**: Swap tools without changing agent logic
- **Debuggability**: Can trace reasoning steps
- **Testability**: Mock tools for unit tests

---

## Tool Abstraction Layer

Tools are **wrappers around external APIs** with a standardized interface.

### Tool Base Class

```python
class Tool(ABC):
    """
    Base tool abstraction.
    
    Tools encapsulate external API calls.
    """
    
    def __init__(self, name: str, description: str):
        self.name = name
        self.description = description
    
    @abstractmethod
    def call(self, input_data, **kwargs) -> ToolResult:
        """Execute the tool."""
        pass
```

### ToolResult Protocol

```python
@dataclass
class ToolResult:
    success: bool
    output: Any
    error: Optional[str] = None
    metadata: Dict[str, Any] = None
```

### Available Tools

#### 1. **STT Tool** (Speech-to-Text)
```python
class GoogleSTTTool(Tool):
    """Google Speech Recognition wrapper."""
    
    def call(self, audio_data):
        # Transcribe audio using Google STT
        # Returns: ToolResult with transcript text
```

#### 2. **LLM Tool** (Gemini)
```python
class GeminiLLMTool(Tool):
    """Google Gemini API wrapper."""
    
    def call(self, prompt, temperature=0.7, max_tokens=2048):
        # Call Gemini API
        # Returns: ToolResult with generated text
```

#### 3. **Sanitizer Tool** (Security)
```python
class SanitizerTool(Tool):
    """Input validation and sanitization."""
    
    def call(self, text_command):
        # Check for malicious patterns
        # Returns: ToolResult with sanitized command
```

### Tool Plugin Architecture

To add a new tool:

```python
# 1. Create tool class
class MyNewTool(Tool):
    def call(self, input_data, **kwargs):
        # Your implementation
        return ToolResult(success=True, output=result)

# 2. Register with agent
agent = CoderAgent()
agent.add_tool(MyNewTool())

# 3. Agent can now use it
result = agent.execute(input_data)
```

---

## Gemini Integration

Voice Cursor uses **Google Gemini 2.0 Flash** at two critical stages:

### 1. Reasoning Agent (Planning)

**Purpose**: Analyze user request and create execution plan

**Prompt Engineering**:
```python
prompt = f"""You are an expert software architect. 
Analyze this coding request and create a detailed execution plan.

User Request: {user_command}

Output a JSON structure with:
1. "command": Brief summary
2. "steps": Array of implementation steps
3. "step_count": Number of steps

Be specific and actionable. Each step should be clear.
"""
```

**Example Input**: "Create a function to validate email addresses"

**Example Output**:
```json
{
  "command": "create email validation function",
  "steps": [
    "Import regex module",
    "Define function signature with type hints",
    "Create regex pattern for email format",
    "Implement validation logic with re.match",
    "Add comprehensive docstring",
    "Include example usage in docstring"
  ],
  "step_count": 6
}
```

**Why This Works**:
- ✅ Gemini's long context window handles complex requests
- ✅ Structured output enables agent coordination
- ✅ Planning before coding improves quality
- ✅ Step-by-step approach reduces errors

### 2. Coder Agent (Generation)

**Purpose**: Generate production-ready code from plan

**Prompt Engineering**:
```python
prompt = f"""You are an expert {language} programmer.
Generate ONLY working, production-ready code.

User Request: {command}

Implementation Plan:
{formatted_steps}

{f"Existing Code to Modify:\n{existing_code}" if existing_code else ""}

Requirements:
- Implement the EXACT user request
- Include all necessary imports
- Add proper error handling
- Use type hints (Python) or types (TypeScript)
- Write clear docstrings/comments
- Follow {language} best practices
- Make code ready to run without modifications

CRITICAL: Return ONLY the code, no explanations, 
no markdown formatting, just pure {language} code.
"""
```

**Example Input**: Plan from Reasoning Agent

**Example Output**: Clean, runnable Python code

**Advanced Gemini Features Used**:
- 🎯 **Code specialization**: 2.0 Flash optimized for programming
- ⚡ **Fast inference**: <3s response time
- 📊 **Structured thinking**: Follows the plan precisely
- 🔄 **Context awareness**: References existing code if provided
- 🌐 **Multi-language**: Supports Python, JS, Go, Rust, etc.

### Prompt Engineering Best Practices

1. **Be Specific**: Tell Gemini exactly what format you want
2. **Use Examples**: Show desired output structure
3. **Set Constraints**: "ONLY code", "NO explanations"
4. **Context First**: Provide plan before asking for code
5. **Temperature Tuning**: 0.7 for creativity with consistency

### Chaining Multiple Gemini Calls

For complex requests, we chain Gemini:

```
User Voice Input
    ↓
Reasoning Agent → Gemini Call #1 (Planning)
    ↓ (execution_plan)
Coder Agent → Gemini Call #2 (Code Generation)
    ↓ (generated_code)
Output
```

**Benefits**:
- 🎯 Better quality through separation
- 🧠 Planning improves code structure
- 🔍 Easier to debug (inspect intermediate plan)
- 📈 Can add more agents for refactoring, testing, etc.

---

## Data Flow

### Complete Pipeline Flow

```
┌──────────────────────────────────────────────────────────┐
│                    User Speaks                           │
└────────────────────┬─────────────────────────────────────┘
                     │ audio_bytes
                     ▼
┌──────────────────────────────────────────────────────────┐
│  Speech Agent                                            │
│  ┌────────────┐                                          │
│  │ Google STT │ → recognizer.recognize_google(audio)     │
│  └────────────┘                                          │
└────────────────────┬─────────────────────────────────────┘
                     │ transcript: "create function..."
                     ▼
┌──────────────────────────────────────────────────────────┐
│  Security Agent                                          │
│  ┌───────────────┐                                       │
│  │ Sanitizer Tool│ → check for malicious patterns        │
│  └───────────────┘                                       │
└────────────────────┬─────────────────────────────────────┘
                     │ validated_command: "create function..."
                     ▼
┌──────────────────────────────────────────────────────────┐
│  Reasoning Agent                                         │
│  ┌─────────────────────────────────┐                    │
│  │ Gemini Tool (Planning)          │                    │
│  │                                 │                    │
│  │ Prompt: "Analyze and create     │                    │
│  │          execution plan..."     │                    │
│  │                                 │                    │
│  │ Returns: {                      │                    │
│  │   "command": "...",             │                    │
│  │   "steps": [...],               │                    │
│  │   "step_count": N               │                    │
│  │ }                               │                    │
│  └─────────────────────────────────┘                    │
└────────────────────┬─────────────────────────────────────┘
                     │ execution_plan
                     ▼
┌──────────────────────────────────────────────────────────┐
│  Coder Agent                                             │
│  ┌─────────────────────────────────┐                    │
│  │ Gemini Tool (Code Generation)   │                    │
│  │                                 │                    │
│  │ Prompt: "Generate production    │                    │
│  │          code for plan..."      │                    │
│  │                                 │                    │
│  │ Returns: "import re\n           │                    │
│  │           def validate_email... │                    │
│  │           ..."                  │                    │
│  └─────────────────────────────────┘                    │
└────────────────────┬─────────────────────────────────────┘
                     │ generated_code
                     ▼
┌──────────────────────────────────────────────────────────┐
│  Validator Agent                                         │
│  ┌────────────┐                                          │
│  │ AST Parser │ → syntax check + save to file            │
│  └────────────┘                                          │
└────────────────────┬─────────────────────────────────────┘
                     │ file_path + status
                     ▼
┌──────────────────────────────────────────────────────────┐
│  Saved to: output_test/generated_code_123.py             │
│  Logs:     logs/agent_calls_2024-01-15_12-30-45.log     │
└──────────────────────────────────────────────────────────┘
```

### Context Object

Context is passed between agents to share state:

```python
context = {
    # User preferences
    "language": "python",         # Target language
    "require_approval": True,     # Review before saving
    
    # File context
    "file_path": "src/main.py",   # Where to save
    "existing_code": "...",       # Code to modify
    
    # Pipeline metadata
    "session_id": "abc-123",      # Track session
    "user_id": "user_456",        # User identifier
}
```

---

## Component Details

### Pipeline Orchestrator

**File**: `pipeline/orchestrator.py`

**Responsibilities**:
- Initialize all agents
- Execute agents sequentially
- Pass context between agents
- Handle errors gracefully
- Log all operations

**Code Structure**:
```python
class VoiceCursorPipeline:
    def __init__(self):
        # Initialize agents
        self.speech_agent = SpeechAgent()
        self.security_agent = SecurityAgent()
        self.reasoning_agent = ReasoningAgent()
        self.coder_agent = CoderAgent()
        self.validator_agent = ValidatorAgent()
        
        # Setup tools for each agent
        self._setup_tools()
    
    def execute(self, audio_input, context):
        # Stage 1: Speech → Text
        speech_result = self.speech_agent.execute(audio_input)
        if not speech_result.success:
            return PipelineResult(success=False, stage="speech")
        
        # Stage 2: Security validation
        security_result = self.security_agent.execute(speech_result.data)
        if not security_result.success:
            return PipelineResult(success=False, stage="security")
        
        # Stage 3: Planning
        reasoning_result = self.reasoning_agent.execute(security_result.data)
        if not reasoning_result.success:
            return PipelineResult(success=False, stage="reasoning")
        
        # Stage 4: Code generation
        coder_result = self.coder_agent.execute(reasoning_result.data, context)
        if not coder_result.success:
            return PipelineResult(success=False, stage="coding")
        
        # Stage 5: Validation
        validator_result = self.validator_agent.execute(coder_result.data)
        
        return PipelineResult(
            success=True,
            stage="complete",
            data=validator_result.data
        )
```

### Logging System

**File**: `utils/logger.py`

**Features**:
- Dual-format logging (text + JSON)
- Per-session log files
- Structured metadata
- Performance tracking

**Usage**:
```python
logger = get_logger()

# Log agent call
logger.log_agent_call(
    agent_name="Reasoning Agent",
    input_data=transcript,
    output_data=plan,
    success=True,
    metadata={"latency_ms": 2500}
)

# Log pipeline events
logger.log_pipeline_start(audio_input)
logger.log_pipeline_end(success=True)
```

### Configuration System

**File**: `config/settings.py`

**Environment Variables**:
```python
# API Keys
GEMINI_API_KEY: str
GROQ_API_KEY: Optional[str]

# Provider selection
LLM_PROVIDER: str = "gemini"
LLM_MODEL: str = "gemini-2.0-flash-exp"
STT_PROVIDER: str = "google"

# Behavior flags
ENABLE_SANITIZER: bool = True
AUTO_FORMAT: bool = True
REQUIRE_APPROVAL: bool = True
```

---

## Extensibility

### Adding New Agents

```python
# 1. Create agent class
from agents.base import Agent, AgentResult

class TestGeneratorAgent(Agent):
    """Generates unit tests for code."""
    
    def __init__(self):
        super().__init__(
            name="Test Generator",
            description="Creates unit tests"
        )
    
    def execute(self, input_data, context=None):
        # input_data = {"code": "...", "language": "python"}
        code = input_data["code"]
        
        # Use LLM tool to generate tests
        llm_tool = self.tools[0]
        prompt = f"Generate pytest tests for:\n{code}"
        result = llm_tool.call(prompt)
        
        return AgentResult(
            success=True,
            data={"tests": result.output},
            metadata={"agent": self.name}
        )

# 2. Add to pipeline
class VoiceCursorPipeline:
    def __init__(self):
        # ... existing agents ...
        self.test_agent = TestGeneratorAgent()
        self.test_agent.add_tool(create_llm_tool())
    
    def execute(self, audio_input, context):
        # ... existing stages ...
        
        # New stage: Generate tests
        if context.get("generate_tests"):
            test_result = self.test_agent.execute(
                {"code": coder_result.data["code"]},
                context
            )
```

### Adding New Tools

```python
# Example: Add Claude API as alternative LLM

from tools.base import Tool, ToolResult

class ClaudeLLMTool(Tool):
    """Anthropic Claude API wrapper."""
    
    def __init__(self):
        super().__init__(
            name="Claude",
            description="Anthropic Claude LLM"
        )
        import anthropic
        self.client = anthropic.Anthropic()
    
    def call(self, prompt, **kwargs):
        response = self.client.messages.create(
            model="claude-3-5-sonnet-20241022",
            max_tokens=2048,
            messages=[{"role": "user", "content": prompt}]
        )
        
        return ToolResult(
            success=True,
            output=response.content[0].text,
            metadata={"model": "claude-3-5-sonnet"}
        )

# Use in agent
def create_llm_tool():
    if settings.LLM_PROVIDER == "claude":
        return ClaudeLLMTool()
    elif settings.LLM_PROVIDER == "gemini":
        return GeminiLLMTool()
```

---

## Performance Considerations

### Latency Breakdown

| Stage | Component | Typical Latency | Optimization |
|-------|-----------|----------------|--------------|
| Speech | Google STT | 1-2s | Use streaming API |
| Security | Sanitizer | <100ms | Regex caching |
| Planning | Gemini API | 2-3s | Batch requests |
| Coding | Gemini API | 3-5s | Reduce context |
| Validation | AST parse | <100ms | Parallel I/O |

### Caching Strategy

```python
# Cache frequently used prompts
from functools import lru_cache

@lru_cache(maxsize=128)
def generate_plan(command: str):
    # Cached Gemini calls for identical commands
    pass
```

### Parallel Execution

For independent operations:
```python
import asyncio

async def execute_parallel():
    # Run validation and testing in parallel
    results = await asyncio.gather(
        validator_agent.execute_async(code),
        test_agent.execute_async(code)
    )
```

---

## Security Architecture

### Input Validation

```python
# Sanitizer checks for:
BLOCKED_PATTERNS = [
    r"eval\(",           # Code injection
    r"exec\(",           # Arbitrary execution
    r"__import__",       # Dynamic imports
    r"subprocess",       # Shell commands
    r"os\.system",       # OS commands
]
```

### Approval Workflow

```python
# Code requires approval before applying
if context.get("require_approval"):
    # Show code to user
    print_code(generated_code)
    
    # Wait for confirmation
    if not Confirm.ask("Apply this code?"):
        return PipelineResult(
            success=False,
            error="User rejected code"
        )
```

---

## Testing Strategy

### Unit Tests
```python
# Test individual agents
def test_reasoning_agent():
    agent = ReasoningAgent()
    agent.add_tool(MockLLMTool())
    
    result = agent.execute("create hello function")
    
    assert result.success
    assert "steps" in result.data
```

### Integration Tests
```python
# Test full pipeline
def test_full_pipeline():
    pipeline = VoiceCursorPipeline()
    
    result = pipeline.execute(
        audio_input="create email validator",
        context={"language": "python"}
    )
    
    assert result.success
    assert result.stage == "complete"
```

---

## Future Architecture Plans

### 1. **Agent Mesh Communication**
- Direct agent-to-agent communication
- Parallel agent execution
- Agent negotiation protocols

### 2. **Self-Improving Agents**
- Eval loops with Gemini
- Agent performance scoring
- Automatic prompt optimization

### 3. **Multi-User Orchestration**
- Shared workspaces
- Collaborative editing
- Agent pooling

### 4. **Edge Deployment**
- Local LLM support (Ollama)
- Offline mode with cached models
- Privacy-first architecture

---

## Resources

- [ReAct Paper](https://arxiv.org/abs/2210.03629)
- [Gemini API Docs](https://ai.google.dev/docs)
- [Multi-Agent Systems](https://en.wikipedia.org/wiki/Multi-agent_system)

---

**Questions?** Open an issue on GitHub or check our [Contributing Guide](CONTRIBUTING.md)
