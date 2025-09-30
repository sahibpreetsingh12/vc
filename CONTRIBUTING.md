# Contributing to Voice Cursor 🤝

Thank you for your interest in contributing to Voice Cursor! This guide will help you get started.

---

## Table of Contents

- [Code of Conduct](#code-of-conduct)
- [Getting Started](#getting-started)
- [Development Setup](#development-setup)
- [How to Contribute](#how-to-contribute)
- [Adding New Agents](#adding-new-agents)
- [Adding New Tools](#adding-new-tools)
- [Code Style Guidelines](#code-style-guidelines)
- [Testing](#testing)
- [Documentation](#documentation)
- [Pull Request Process](#pull-request-process)

---

## Code of Conduct

### Our Pledge

We are committed to providing a welcoming and inspiring community for all. Please be respectful and constructive in your interactions.

### Expected Behavior

- ✅ Be respectful and inclusive
- ✅ Welcome newcomers
- ✅ Focus on constructive feedback
- ✅ Assume good intentions

### Unacceptable Behavior

- ❌ Harassment or discrimination
- ❌ Trolling or inflammatory comments
- ❌ Personal attacks
- ❌ Publishing others' private information

---

## Getting Started

### Prerequisites

- Python 3.8 or higher
- Git
- Gemini API key ([Get one free](https://aistudio.google.com/app/apikey))
- Basic understanding of multi-agent systems (helpful but not required)

### Quick Setup

```bash
# 1. Fork and clone the repository
git clone https://github.com/YOUR_USERNAME/voice-cursor.git
cd voice-cursor

# 2. Create virtual environment
python3 -m venv venv
source venv/bin/activate  # On Windows: venv\Scripts\activate

# 3. Install dependencies (including dev dependencies)
pip install -r requirements.txt
pip install -r requirements-dev.txt  # If available

# 4. Set up environment
cp .env.example .env
# Edit .env and add your GEMINI_API_KEY

# 5. Run tests to verify setup
pytest tests/ -v

# 6. Try the system
python test_3_agents.py
```

---

## Development Setup

### IDE Configuration

**VS Code (Recommended)**
```json
{
  "python.linting.enabled": true,
  "python.linting.pylintEnabled": true,
  "python.formatting.provider": "black",
  "python.formatting.blackArgs": ["--line-length", "100"],
  "editor.formatOnSave": true
}
```

**PyCharm**
- Enable Black formatter: Settings → Tools → Black
- Enable pylint: Settings → Tools → External Tools

### Pre-commit Hooks

```bash
# Install pre-commit
pip install pre-commit

# Set up hooks
pre-commit install

# Run manually
pre-commit run --all-files
```

---

## How to Contribute

### Types of Contributions

1. **🐛 Bug Reports**: Found a bug? Open an issue!
2. **✨ Feature Requests**: Have an idea? We'd love to hear it!
3. **📝 Documentation**: Improve docs, add examples
4. **💻 Code**: Fix bugs, add features, improve performance
5. **🧪 Tests**: Add test coverage
6. **🎨 UI/UX**: Improve the web IDE

### Finding Issues

- Check [Issues](https://github.com/yourusername/voice-cursor/issues) for bugs and features
- Look for issues labeled `good first issue` or `help wanted`
- Ask in [Discussions](https://github.com/yourusername/voice-cursor/discussions) if unsure

---

## Adding New Agents

Agents are the core of Voice Cursor. Here's how to add a new one:

### 1. Create Agent Class

Create a new file in `agents/` directory:

```python
# agents/my_new_agent.py

"""
My New Agent - Brief description of what it does.

This agent handles [specific responsibility].
"""

from typing import Any, Dict, Optional
from .base import Agent, AgentResult


class MyNewAgent(Agent):
    """
    Detailed description of the agent.
    
    This agent performs [specific task] using [tools].
    It fits into the pipeline at [stage].
    
    Example:
        ```python
        agent = MyNewAgent()
        agent.add_tool(SomeTool())
        result = agent.execute(input_data)
        ```
    """
    
    def __init__(self):
        super().__init__(
            name="My New Agent",
            description="Short description for logging"
        )
    
    def execute(self, input_data: Any, context: Optional[Dict] = None) -> AgentResult:
        """
        Execute the agent's main logic.
        
        Args:
            input_data: Description of expected input format
            context: Optional context with additional parameters
            
        Returns:
            AgentResult with:
                - success: bool
                - data: Output data (describe format)
                - error: Error message if failed
                - metadata: Agent name, tool used, etc.
                
        Raises:
            ValueError: If input_data is invalid
        """
        try:
            # 1. Validate input
            if not self._validate_input(input_data):
                return AgentResult(
                    success=False,
                    data=None,
                    error="Invalid input format"
                )
            
            # 2. Check tools are available
            if not self.tools:
                return AgentResult(
                    success=False,
                    data=None,
                    error="No tools configured for this agent"
                )
            
            # 3. Execute core logic using tools
            tool = self.tools[0]
            result = tool.call(input_data)
            
            if not result.success:
                return AgentResult(
                    success=False,
                    data=None,
                    error=f"Tool execution failed: {result.error}"
                )
            
            # 4. Process tool output
            processed_data = self._process_output(result.output)
            
            # 5. Return success result
            return AgentResult(
                success=True,
                data=processed_data,
                metadata={
                    "agent": self.name,
                    "tool_used": tool.name,
                    # Add any other relevant metadata
                }
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data=None,
                error=f"{self.name} error: {str(e)}"
            )
    
    def _validate_input(self, input_data: Any) -> bool:
        """Validate input data format."""
        # Add validation logic
        return True
    
    def _process_output(self, output: Any) -> Any:
        """Process tool output into desired format."""
        # Add processing logic
        return output
```

### 2. Add Agent to Pipeline

Edit `pipeline/orchestrator.py`:

```python
from agents.my_new_agent import MyNewAgent

class VoiceCursorPipeline:
    def __init__(self):
        # ... existing agents ...
        self.my_new_agent = MyNewAgent()
        self._setup_tools()
    
    def _setup_tools(self):
        # ... existing tool setup ...
        
        # Setup tools for new agent
        self.my_new_agent.add_tool(create_appropriate_tool())
    
    def execute(self, audio_input, context):
        # ... existing stages ...
        
        # Add new stage
        if context.get("enable_my_feature"):
            my_result = self.my_new_agent.execute(
                previous_result.data,
                context
            )
            
            if not my_result.success:
                return PipelineResult(
                    success=False,
                    stage="my_new_stage",
                    error=my_result.error
                )
```

### 3. Add Tests

Create `tests/test_my_new_agent.py`:

```python
import pytest
from agents.my_new_agent import MyNewAgent
from tools.base import Tool, ToolResult


class MockTool(Tool):
    """Mock tool for testing."""
    def __init__(self):
        super().__init__("Mock Tool", "Test tool")
    
    def call(self, input_data, **kwargs):
        return ToolResult(
            success=True,
            output={"result": "mocked"}
        )


def test_my_new_agent_success():
    """Test successful execution."""
    agent = MyNewAgent()
    agent.add_tool(MockTool())
    
    result = agent.execute({"test": "data"})
    
    assert result.success
    assert result.data is not None
    assert result.error is None


def test_my_new_agent_no_tools():
    """Test error when no tools configured."""
    agent = MyNewAgent()
    
    result = agent.execute({"test": "data"})
    
    assert not result.success
    assert "No tools" in result.error


def test_my_new_agent_invalid_input():
    """Test error handling for invalid input."""
    agent = MyNewAgent()
    agent.add_tool(MockTool())
    
    result = agent.execute(None)
    
    assert not result.success
    assert "Invalid input" in result.error
```

### 4. Document the Agent

Add to documentation:

```markdown
# My New Agent

## Purpose
Describe what the agent does and why it's useful.

## Input Format
```python
{
    "field1": "value",
    "field2": 123
}
```

## Output Format
```python
{
    "result": "processed_data",
    "metadata": {}
}
```

## Usage Example
```python
agent = MyNewAgent()
agent.add_tool(RequiredTool())
result = agent.execute(input_data)
```

## Configuration
List any environment variables or settings.
```

---

## Adding New Tools

Tools wrap external APIs and services.

### 1. Create Tool Class

Create a new file in `tools/` directory:

```python
# tools/my_new_tool.py

"""
My New Tool - Integration with [External Service].
"""

from typing import Any, Dict, Optional
from .base import Tool, ToolResult


class MyNewTool(Tool):
    """
    Wrapper for [External Service] API.
    
    This tool provides [functionality] by calling [API].
    
    Attributes:
        api_key: Authentication key for the service
        endpoint: API endpoint URL
    
    Example:
        ```python
        tool = MyNewTool(api_key="your_key")
        result = tool.call({"query": "data"})
        if result.success:
            print(result.output)
        ```
    """
    
    def __init__(self, api_key: Optional[str] = None):
        super().__init__(
            name="My New Tool",
            description="Integration with [External Service]"
        )
        self.api_key = api_key or self._get_api_key()
        self.client = None  # Lazy initialization
    
    def _get_api_key(self) -> str:
        """Get API key from environment or config."""
        from config import settings
        return getattr(settings, 'MY_SERVICE_API_KEY', '')
    
    def _get_client(self):
        """Lazy initialization of API client."""
        if self.client is None:
            # Initialize client
            import external_service
            self.client = external_service.Client(api_key=self.api_key)
        return self.client
    
    def call(self, input_data: Any, **kwargs) -> ToolResult:
        """
        Execute the tool with given input.
        
        Args:
            input_data: Input data for the tool
            **kwargs: Additional parameters
                - param1: Description
                - param2: Description
        
        Returns:
            ToolResult with:
                - success: Whether call succeeded
                - output: Response from API
                - error: Error message if failed
                - metadata: API metadata (timing, tokens, etc.)
        
        Raises:
            ValueError: If input_data is invalid
        """
        try:
            # 1. Validate input
            if not input_data:
                return ToolResult(
                    success=False,
                    output=None,
                    error="Input data is required"
                )
            
            # 2. Get client
            client = self._get_client()
            
            # 3. Make API call
            response = client.api_method(
                input_data,
                param1=kwargs.get('param1', 'default'),
                param2=kwargs.get('param2', 100)
            )
            
            # 4. Process response
            output = self._process_response(response)
            
            # 5. Return success result
            return ToolResult(
                success=True,
                output=output,
                metadata={
                    "tool": self.name,
                    "api_version": response.version,
                    "latency_ms": response.latency
                }
            )
            
        except Exception as e:
            return ToolResult(
                success=False,
                output=None,
                error=f"API call failed: {str(e)}"
            )
    
    def _process_response(self, response) -> Any:
        """Process API response into standard format."""
        # Transform response as needed
        return response.data
```

### 2. Register Tool

Add factory function in `tools/__init__.py`:

```python
from .my_new_tool import MyNewTool

def create_my_new_tool() -> MyNewTool:
    """Create and configure MyNewTool."""
    return MyNewTool()
```

### 3. Add Tests

```python
# tests/test_my_new_tool.py

import pytest
from unittest.mock import Mock, patch
from tools.my_new_tool import MyNewTool


def test_my_new_tool_success():
    """Test successful API call."""
    tool = MyNewTool(api_key="test_key")
    
    with patch.object(tool, '_get_client') as mock_client:
        mock_client.return_value.api_method.return_value = Mock(
            version="1.0",
            latency=100,
            data={"result": "success"}
        )
        
        result = tool.call({"query": "test"})
        
        assert result.success
        assert result.output == {"result": "success"}
        assert result.metadata["latency_ms"] == 100


def test_my_new_tool_error():
    """Test error handling."""
    tool = MyNewTool(api_key="test_key")
    
    result = tool.call(None)
    
    assert not result.success
    assert "required" in result.error.lower()
```

---

## Code Style Guidelines

### Python Style

We follow **PEP 8** with some modifications:

```python
# Line length: 100 characters (not 79)
MAX_LINE_LENGTH = 100

# Use double quotes for strings
message = "Hello, world!"

# Type hints are required
def process_data(input_data: Dict[str, Any], count: int = 10) -> List[str]:
    pass

# Docstrings use Google style
def example_function(param1: str, param2: int) -> bool:
    """
    Brief description of function.
    
    Longer description if needed. Explain the purpose,
    behavior, and any important details.
    
    Args:
        param1: Description of param1
        param2: Description of param2
    
    Returns:
        Description of return value
    
    Raises:
        ValueError: When param1 is empty
        TypeError: When param2 is not an integer
    
    Example:
        ```python
        result = example_function("test", 42)
        print(result)  # True
        ```
    """
    pass
```

### Naming Conventions

```python
# Classes: PascalCase
class MyAgent:
    pass

# Functions/methods: snake_case
def process_audio(audio_data):
    pass

# Constants: UPPER_SNAKE_CASE
MAX_RETRIES = 3
API_ENDPOINT = "https://api.example.com"

# Private methods: _leading_underscore
def _internal_helper():
    pass

# "Protected" attributes: _leading_underscore
class Agent:
    def __init__(self):
        self._internal_state = {}
```

### Import Organization

```python
# 1. Standard library imports
import os
import sys
from typing import Any, Dict, Optional

# 2. Third-party imports
import google.generativeai as genai
from rich.console import Console

# 3. Local imports
from agents.base import Agent, AgentResult
from tools.llm_tool import GeminiLLMTool
from config import settings
```

### Error Handling

```python
# Use specific exceptions
try:
    result = risky_operation()
except FileNotFoundError as e:
    logger.error(f"File not found: {e}")
    return AgentResult(success=False, error=f"File error: {e}")
except ValueError as e:
    logger.error(f"Invalid value: {e}")
    return AgentResult(success=False, error=f"Validation error: {e}")
except Exception as e:
    logger.error(f"Unexpected error: {e}")
    return AgentResult(success=False, error=f"System error: {e}")

# Always return AgentResult or ToolResult
def execute(self, input_data):
    # Never raise exceptions that escape agent boundaries
    try:
        # ... logic ...
        return AgentResult(success=True, data=result)
    except Exception as e:
        return AgentResult(success=False, error=str(e))
```

---

## Testing

### Test Structure

```
tests/
├── __init__.py
├── conftest.py              # Shared fixtures
├── test_agents/
│   ├── test_speech_agent.py
│   ├── test_reasoning_agent.py
│   └── test_coder_agent.py
├── test_tools/
│   ├── test_llm_tool.py
│   └── test_stt_tool.py
└── test_pipeline/
    └── test_orchestrator.py
```

### Writing Tests

```python
import pytest
from unittest.mock import Mock, patch


@pytest.fixture
def sample_input():
    """Fixture providing sample input data."""
    return {"command": "create function", "language": "python"}


def test_agent_with_fixture(sample_input):
    """Test using fixture."""
    agent = MyAgent()
    result = agent.execute(sample_input)
    assert result.success


@pytest.mark.integration
def test_full_pipeline():
    """Integration test for complete pipeline."""
    # Tests marked as integration can be run separately
    pass


@patch('tools.llm_tool.genai')
def test_with_mock(mock_genai):
    """Test using mocks to avoid API calls."""
    mock_genai.GenerativeModel.return_value.generate_content.return_value.text = "code"
    
    tool = GeminiLLMTool()
    result = tool.call("test prompt")
    
    assert result.success
    assert result.output == "code"
```

### Running Tests

```bash
# Run all tests
pytest

# Run with verbose output
pytest -v

# Run specific test file
pytest tests/test_agents/test_reasoning_agent.py

# Run tests matching pattern
pytest -k "test_agent"

# Run with coverage
pytest --cov=agents --cov=tools --cov-report=html

# Run only unit tests (skip integration)
pytest -m "not integration"
```

---

## Documentation

### Code Documentation

- Every public class and function needs a docstring
- Use Google-style docstrings
- Include examples for complex functionality
- Document exceptions that can be raised

### README Updates

When adding features, update:
- Features list
- Usage examples
- Configuration options
- Troubleshooting section

### Architecture Documentation

For significant changes:
- Update `ARCHITECTURE.md`
- Add diagrams if helpful
- Explain design decisions

---

## Pull Request Process

### 1. Create a Branch

```bash
# Create feature branch
git checkout -b feature/my-new-feature

# Or bugfix branch
git checkout -b bugfix/fix-something
```

### 2. Make Changes

- Write code following style guidelines
- Add tests for new functionality
- Update documentation
- Ensure all tests pass

### 3. Commit Changes

```bash
# Stage changes
git add .

# Commit with descriptive message
git commit -m "feat: Add new agent for X

- Implement MyNewAgent class
- Add tests with 95% coverage
- Update documentation with examples

Closes #123"
```

**Commit Message Format:**
```
<type>: <subject>

<body>

<footer>
```

**Types:**
- `feat`: New feature
- `fix`: Bug fix
- `docs`: Documentation only
- `style`: Code style changes
- `refactor`: Code refactoring
- `test`: Adding tests
- `chore`: Maintenance tasks

### 4. Push and Create PR

```bash
# Push to your fork
git push origin feature/my-new-feature

# Go to GitHub and create Pull Request
```

### 5. PR Description Template

```markdown
## Description
Brief description of changes.

## Type of Change
- [ ] Bug fix
- [ ] New feature
- [ ] Breaking change
- [ ] Documentation update

## Testing
- [ ] Unit tests added/updated
- [ ] Integration tests pass
- [ ] Manual testing completed

## Checklist
- [ ] Code follows style guidelines
- [ ] Self-review completed
- [ ] Documentation updated
- [ ] Tests added and passing
- [ ] No breaking changes (or documented)

## Related Issues
Closes #123
Relates to #456
```

### 6. Review Process

- Maintainers will review within 3-5 days
- Address feedback by pushing new commits
- Once approved, PR will be merged

---

## Getting Help

- **Questions?** Ask in [Discussions](https://github.com/yourusername/voice-cursor/discussions)
- **Bug?** Open an [Issue](https://github.com/yourusername/voice-cursor/issues)
- **Chat?** Join our Discord (if available)

---

## Recognition

Contributors will be:
- Listed in `CONTRIBUTORS.md`
- Credited in release notes
- Eligible for maintainer role with sustained contributions

---

Thank you for contributing to Voice Cursor! 🎉
