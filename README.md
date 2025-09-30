# 🎙️ Voice Cursor

<div align="center">

**Speak Your Code Into Existence**

*A multi-agent voice-first development system powered by Google Gemini AI*

[![Python 3.8+](https://img.shields.io/badge/python-3.8+-blue.svg)](https://www.python.org/downloads/)
[![Gemini API](https://img.shields.io/badge/Gemini-2.0_Flash-orange.svg)](https://ai.google.dev/)
[![License: MIT](https://img.shields.io/badge/License-MIT-green.svg)](LICENSE)
[![Code style: black](https://img.shields.io/badge/code%20style-black-000000.svg)](https://github.com/psf/black)

[Features](#-features) • [Quick Start](#-quick-start) • [Architecture](#-architecture) • [Demo](#-demo) • [Documentation](#-documentation)

</div>

---

## 🎯 What is Voice Cursor?

Voice Cursor is an **intelligent voice-to-code IDE** that transforms natural speech into production-ready code. Simply speak your intent, and watch as a sophisticated multi-agent system powered by Google Gemini AI:

1. 🎤 **Transcribes** your voice with Google Speech-to-Text
2. 🛡️ **Validates** safety with security checks
3. 🧠 **Plans** implementation using Gemini 2.0 Flash
4. 👨‍💻 **Generates** clean, working code with Gemini
5. ✅ **Validates** and saves to your workspace
6. 📊 **Logs** every step for observability

### 🎬 Demo Video

> 📹 **Demo coming soon**: Watch Voice Cursor transform speech into working Python code in real-time

---

## ✨ Features

### 🧠 **Advanced Gemini Integration**
- **Dual-agent Gemini usage**: Separate reasoning and code generation phases
- **Context-aware planning**: Gemini analyzes requirements and creates step-by-step execution plans
- **Intelligent code synthesis**: Gemini generates production-ready code with best practices
- **Prompt engineering**: Carefully crafted prompts for optimal output quality
- **Multi-turn reasoning**: Agents can chain Gemini calls for complex tasks

### 🏗️ **Multi-Agent Architecture**
- **5 specialized agents**: Speech, Security, Reasoning, Coder, Validator
- **ReAct pattern**: Agents reason about actions before execution
- **Tool abstraction**: Pluggable API wrappers for easy provider switching
- **Clean separation of concerns**: Each agent has a single responsibility
- **Extensible design**: Add new agents/tools without modifying core system

### 🎙️ **Voice-First Development**
- **Real-time speech capture**: Works with any microphone
- **Google STT integration**: High-accuracy transcription
- **Natural language understanding**: Speak naturally, no special commands
- **Web IDE**: Browser-based interface with VS Code-like features

### 🔒 **Security & Safety**
- **Input sanitization**: Prevents malicious code injection
- **Command validation**: Blocks unsafe operations
- **Approval workflows**: Review code before applying changes

### 📊 **Observability & Debugging**
- **Structured logging**: JSON + text logs for every agent call
- **Performance tracking**: Measure latency at each pipeline stage
- **Error tracing**: Detailed error context for debugging
- **Replay capability**: Analyze past executions

---

## 🚀 Quick Start

### Prerequisites
- Python 3.8 or higher
- Microphone access
- Internet connection
- [Gemini API key](https://aistudio.google.com/app/apikey) (free tier available)

### Installation (3 steps)

#### 1️⃣ Clone and Install Dependencies

```bash
git clone https://github.com/yourusername/voice-cursor.git
cd voice-cursor
pip install -r requirements.txt
```

#### 2️⃣ Configure API Keys

```bash
# Copy environment template
cp .env.example .env

# Edit .env and add your Gemini API key
# Get a free key: https://aistudio.google.com/app/apikey
```

**Your `.env` should contain:**
```bash
GEMINI_API_KEY=your_actual_key_here
LLM_PROVIDER=gemini
LLM_MODEL=gemini-2.0-flash-exp
```

#### 3️⃣ Run the System

**Terminal Mode:**
```bash
python test_3_agents.py
```

**Web IDE Mode:**
```bash
python web_ide.py
# Open http://localhost:5000 in your browser
```

### First Run

1. When prompted, press **Enter** to start recording
2. Speak clearly: *"Create a function to calculate fibonacci numbers"*
3. Wait 5-10 seconds while agents process your request
4. Find generated code in `output_test/`
5. Check logs in `logs/` for detailed execution trace

---

## 🏗️ Architecture

### System Overview

```
┌─────────────────────────────────────────────────────────────┐
│                     Voice Cursor Pipeline                    │
└─────────────────────────────────────────────────────────────┘

  🎤 Voice Input
       │
       ▼
 ┌──────────────┐
 │ Speech Agent │ → Google STT API
 └──────────────┘
       │ transcript
       ▼
 ┌──────────────┐
 │Security Agent│ → Sanitizer Tool
 └──────────────┘
       │ validated_command
       ▼
 ┌──────────────┐
 │Reasoning Agent│ → Gemini 2.0 Flash (Planning)
 └──────────────┘
       │ execution_plan
       ▼
 ┌──────────────┐
 │ Coder Agent  │ → Gemini 2.0 Flash (Code Generation)
 └──────────────┘
       │ generated_code
       ▼
 ┌──────────────┐
 │Validator Agent│ → Syntax Check + File I/O
 └──────────────┘
       │
       ▼
  💾 Saved File + 📊 Logs
```

### Agent Responsibilities

| Agent | Purpose | Tools Used | Input | Output |
|-------|---------|------------|-------|--------|
| **Speech Agent** | Transcribe voice to text | Google STT | Audio bytes | Text transcript |
| **Security Agent** | Validate command safety | Sanitizer | Text command | Sanitized command |
| **Reasoning Agent** | Create execution plan | Gemini 2.0 Flash | Command | Step-by-step plan |
| **Coder Agent** | Generate code | Gemini 2.0 Flash | Plan + Context | Python/JS code |
| **Validator Agent** | Review and save | AST Parser | Code | File path |

### Gemini Integration Details

**1. Reasoning Agent - Planning Phase**
```python
# Gemini analyzes the user request and creates a structured plan
Prompt: "Analyze this coding request and create a step-by-step plan..."
Output: {
  "command": "create fibonacci function",
  "steps": [
    "Define function signature",
    "Implement recursive logic",
    "Add base cases",
    "Include docstring"
  ],
  "step_count": 4
}
```

**2. Coder Agent - Generation Phase**
```python
# Gemini generates actual code following the plan
Prompt: "Generate production-ready Python code for: {plan}"
Output: Complete, runnable Python code with imports, docs, error handling
```

**Key Gemini Features Utilized:**
- ✅ **Long context window**: Handle complex multi-step plans
- ✅ **Code generation specialization**: Optimized for programming tasks
- ✅ **Fast inference**: 2.0 Flash model for real-time responses
- ✅ **Structured output**: JSON-parseable plans for agent coordination
- ✅ **Multi-language support**: Python, JavaScript, Go, Rust, etc.

---

## 📂 Project Structure

```
voice-cursor/
├── agents/                      # 🤖 AI Agents
│   ├── base.py                  # Base agent abstraction
│   ├── speech_agent.py          # Voice → Text
│   ├── security_agent.py        # Input validation
│   ├── reasoning_agent.py       # Planning with Gemini
│   ├── coder_agent.py           # Code generation with Gemini
│   └── validator_agent.py       # Code review
│
├── tools/                       # 🔧 API Wrappers
│   ├── base.py                  # Tool abstraction
│   ├── stt_tool.py              # Google Speech-to-Text
│   ├── llm_tool.py              # Gemini API wrapper
│   └── sanitizer_tool.py        # Security checks
│
├── pipeline/                    # 🔄 Orchestration
│   ├── __init__.py
│   └── orchestrator.py          # Multi-agent coordinator
│
├── utils/                       # 🛠️ Utilities
│   ├── logger.py                # Structured logging
│   └── observability.py         # Performance tracking
│
├── config/                      # ⚙️ Configuration
│   ├── __init__.py
│   └── settings.py              # Environment variables
│
├── templates/                   # 🎨 Web UI
│   └── index.html              # Voice IDE interface
│
├── static/                      # 📦 Frontend assets
│   └── css/                    # Stylesheets
│
├── output_test/                 # 💾 Generated code
├── logs/                        # 📊 Agent logs
│
├── test_3_agents.py            # 🎯 Main CLI entry point
├── web_ide.py                  # 🌐 Web server
├── main.py                     # 🐍 Python API
│
├── requirements.txt            # 📦 Dependencies
├── .env.example               # 🔑 API key template
├── .gitignore                 # 🚫 Git exclusions
│
└── docs/                       # 📚 Documentation
    ├── SETUP.md               # Detailed setup guide
    ├── ARCHITECTURE.md        # System design
    ├── API.md                 # API reference
    └── CONTRIBUTING.md        # Contribution guidelines
```

---

## 💡 Usage Examples

### Example 1: Simple Function

**Voice Input:**
> "Create a function to validate email addresses"

**Generated Code:**
```python
import re

def validate_email(email: str) -> bool:
    """
    Validate email address format.
    
    Args:
        email: Email address to validate
        
    Returns:
        True if valid, False otherwise
    """
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return re.match(pattern, email) is not None
```

### Example 2: Class with Methods

**Voice Input:**
> "Write a class to manage a shopping cart with add, remove, and total methods"

**Generated Code:**
```python
from typing import Dict, List

class ShoppingCart:
    """
    A shopping cart for managing items and calculating totals.
    """
    
    def __init__(self):
        self.items: Dict[str, Dict] = {}
    
    def add_item(self, name: str, price: float, quantity: int = 1):
        """Add item to cart."""
        if name in self.items:
            self.items[name]['quantity'] += quantity
        else:
            self.items[name] = {'price': price, 'quantity': quantity}
    
    def remove_item(self, name: str):
        """Remove item from cart."""
        if name in self.items:
            del self.items[name]
    
    def get_total(self) -> float:
        """Calculate cart total."""
        return sum(item['price'] * item['quantity'] 
                   for item in self.items.values())
```

### Example 3: API Endpoint

**Voice Input:**
> "Build a FastAPI endpoint to fetch user data by ID"

**Generated Code:**
```python
from fastapi import FastAPI, HTTPException
from pydantic import BaseModel
from typing import Optional

app = FastAPI()

class User(BaseModel):
    id: int
    name: str
    email: str

# Mock database
USERS_DB = {
    1: User(id=1, name="Alice", email="alice@example.com"),
    2: User(id=2, name="Bob", email="bob@example.com"),
}

@app.get("/users/{user_id}", response_model=User)
async def get_user(user_id: int):
    """
    Fetch user by ID.
    
    Args:
        user_id: User identifier
        
    Returns:
        User object
        
    Raises:
        HTTPException: If user not found
    """
    if user_id not in USERS_DB:
        raise HTTPException(status_code=404, detail="User not found")
    return USERS_DB[user_id]
```

---

## 🧪 Testing

```bash
# Run all tests
pytest tests/ -v

# Run specific test suite
pytest tests/test_agents.py -v

# Run with coverage
pytest --cov=agents --cov=tools --cov=pipeline

# Test individual agent
python -c "from agents.speech_agent import SpeechAgent; print('✅ Import successful')"
```

---

## 🐛 Troubleshooting

### Common Issues

<details>
<summary><b>"GEMINI_API_KEY not found"</b></summary>

**Solution:**
```bash
# Check .env exists
ls -la .env

# Verify key is set
cat .env | grep GEMINI_API_KEY

# If missing, add it
echo "GEMINI_API_KEY=your_key_here" >> .env
```
</details>

<details>
<summary><b>"No module named 'speech_recognition'"</b></summary>

**Solution:**
```bash
pip install -r requirements.txt

# If persists, reinstall
pip install --force-reinstall speech_recognition
```
</details>

<details>
<summary><b>Microphone not detected</b></summary>

**macOS:**
- Go to System Preferences → Security & Privacy → Microphone
- Allow Terminal/iTerm access

**Linux:**
```bash
sudo apt-get install python3-pyaudio portaudio19-dev
pip install --upgrade pyaudio
```

**Windows:**
```bash
pip install pipwin
pipwin install pyaudio
```
</details>

<details>
<summary><b>"Could not understand audio"</b></summary>

- Speak more clearly and slowly
- Reduce background noise
- Move closer to microphone
- Check microphone is not muted
- Test: `python -c "import speech_recognition as sr; print(sr.Microphone.list_microphone_names())"`
</details>

---

## 📚 Documentation

- **[Setup Guide](SETUP.md)** - Detailed installation and configuration
- **[Architecture](ARCHITECTURE.md)** - System design and patterns
- **[API Reference](docs/API.md)** - Agent and tool documentation
- **[Contributing](CONTRIBUTING.md)** - How to extend the system
- **[New User Guide](NEW_USER_GUIDE.md)** - Step-by-step checklist
- **[Voice IDE Guide](VOICE_IDE_GUIDE.md)** - Web interface documentation

---

## 🤝 Contributing

We welcome contributions! Voice Cursor is designed to be **easily extensible**:

### Adding a New Agent

```python
from agents.base import Agent, AgentResult

class MyCustomAgent(Agent):
    def __init__(self):
        super().__init__(
            name="My Agent",
            description="Does something cool"
        )
    
    def execute(self, input_data, context=None):
        # Your logic here
        return AgentResult(
            success=True,
            data=result,
            metadata={"agent": self.name}
        )
```

### Adding a New Tool

```python
from tools.base import Tool, ToolResult

class MyCustomTool(Tool):
    def __init__(self):
        super().__init__(
            name="My Tool",
            description="Calls external API"
        )
    
    def call(self, input_data, **kwargs):
        # API call logic
        return ToolResult(
            success=True,
            output=response
        )
```

See [CONTRIBUTING.md](CONTRIBUTING.md) for detailed guidelines.

---

## 🎯 Roadmap

- [ ] **Multi-language support**: Add support for JavaScript, Go, Rust
- [ ] **IDE integrations**: VS Code extension, Cursor plugin
- [ ] **Voice commands**: "refactor this function", "add tests"
- [ ] **Code review agent**: Automated code quality checks
- [ ] **Deployment agent**: Push code to GitHub, deploy to cloud
- [ ] **Team collaboration**: Shared workspaces, voice pair programming
- [ ] **Gemini multimodal**: Analyze screenshots, diagrams

---

## 📊 Performance

**Typical Latency (end-to-end):**
- Speech transcription: ~1-2s
- Security validation: <0.1s
- Gemini planning: ~2-3s
- Gemini code generation: ~3-5s
- Validation + save: <0.1s
- **Total: ~6-10 seconds**

**Resource Usage:**
- Memory: ~100-200MB
- API costs: Free tier sufficient for development
- Network: Requires stable internet connection

---

## 🔗 Tech Stack

- **AI/ML**: Google Gemini 2.0 Flash, Google Speech-to-Text
- **Language**: Python 3.8+
- **Web Framework**: Flask, Flask-SocketIO
- **Audio Processing**: SpeechRecognition, PyAudio
- **CLI**: Rich (terminal UI)
- **Config**: python-dotenv, Pydantic
- **Testing**: pytest, pytest-cov
- **Code Quality**: black, pylint, mypy

---

## 📄 License

MIT License - see [LICENSE](LICENSE) for details

---

## 🙏 Acknowledgments

- **Google Gemini AI** - For powerful code generation capabilities
- **Google Cloud Speech-to-Text** - For accurate voice transcription
- **ReAct Pattern** - For multi-agent reasoning framework

---

## 📬 Contact

- **Issues**: [GitHub Issues](https://github.com/yourusername/voice-cursor/issues)
- **Discussions**: [GitHub Discussions](https://github.com/yourusername/voice-cursor/discussions)
- **Email**: your.email@example.com

---

<div align="center">

**Built with ❤️ for the Google AI Hackathon**

⭐ **Star this repo** if you find it useful!

[Report Bug](https://github.com/yourusername/voice-cursor/issues) · [Request Feature](https://github.com/yourusername/voice-cursor/issues) · [View Demo](#)

</div>
