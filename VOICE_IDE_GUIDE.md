# 🎙️ Voice First IDE - Quick Start Guide

## Overview

Voice First IDE is a revolutionary code editor that lets you develop software using natural voice commands. It features:

- **📁 VS Code-like Interface**: Familiar three-panel layout
- **🎤 Voice-First Development**: Speak your coding intentions
- **🤖 AI Agent Pipeline**: Multi-agent system (Speech → Security → Reasoning → Coder)
- **✨ Monaco Editor**: Full syntax highlighting and IntelliSense
- **⚡ Real-time Updates**: WebSocket-based live agent status

---

## Installation

### 1. Install Dependencies

```bash
pip install -r requirements.txt
```

### 2. Set Up API Keys

Create a `.env` file (or copy from `.env.example`):

```bash
cp .env.example .env
```

Edit `.env` and add your Gemini API key:

```bash
GEMINI_API_KEY=your_gemini_api_key_here
```

Get a free API key at: https://aistudio.google.com/app/apikey

---

## Running the IDE

### Start the Web Server

```bash
python web_ide.py
```

You should see:

```
🎙️ Voice First IDE Starting...
📁 Workspace: /your/current/directory
🌐 Open http://localhost:5000 in your browser
```

### Open in Browser

Navigate to **http://localhost:5000** in your web browser (Chrome recommended).

---

## Interface Overview

```
┌──────────────────────────────────────────────────────────────┐
│  🎙️ Voice First IDE          📁 Workspace         ● Connected│
├───────────┬─────────────────────────────┬──────────────────────┤
│           │                             │                      │
│  📁 Files │    📝 Code Editor          │  💬 Voice Chat       │
│           │                             │                      │
│  • file1  │    [Monaco Editor]          │  🎤 Speech Agent     │
│  • file2  │    with syntax              │  🛡️ Security Agent   │
│  📂 folder│    highlighting             │  🧠 Reasoning Agent  │
│           │                             │  👨‍💻 Coder Agent      │
│           │                             │                      │
│           │                             │  [Conversation]      │
│           │                             │                      │
│           │                             │  [Type or 🎤]        │
└───────────┴─────────────────────────────┴──────────────────────┘
```

### Left Panel - File Explorer
- Browse your workspace files and folders
- Click to open files in the editor
- Create new files with the + button
- Refresh with the ↻ button

### Center Panel - Code Editor
- **Monaco Editor** (same as VS Code)
- Full syntax highlighting
- IntelliSense and autocomplete
- **Save**: `Ctrl+S` (Windows/Linux) or `Cmd+S` (Mac)
- Multiple language support

### Right Panel - Voice Assistant
- **Agent Status**: Real-time pipeline progress
- **Conversation**: Chat history with the AI
- **Text Input**: Type commands directly
- **Microphone Button**: Click to speak (voice input)

---

## How to Use Voice Commands

### 1. Type a Command (Recommended for Testing)

In the text input box at the bottom right, type:

```
Create a function to calculate fibonacci numbers
```

Press **Enter** or click the **Send** button.

### 2. Use Voice Input

1. Click the **microphone button** (large gradient button)
2. Speak your command clearly
3. Click again to stop recording
4. The AI will process your voice

**Note**: Voice recording captures audio, but for full STT (Speech-to-Text) functionality, you may need to integrate with your STT API backend.

---

## Example Commands

Try these voice/text commands:

### Creating New Code

```
Create a function to validate email addresses
```

```
Write a class to manage a todo list with add, remove, and list methods
```

```
Generate a Flask API endpoint to fetch user data from a database
```

### Modifying Existing Code

1. First, open a file from the file explorer
2. Then give commands like:

```
Add error handling to this function
```

```
Refactor this code to use async/await
```

```
Add docstrings to all functions in this file
```

---

## Agent Pipeline

When you submit a command, watch the agent status indicators on the right:

### 🎤 Speech Agent
- Converts voice/text to transcribed command
- Status: `idle` → `processing` → `completed`

### 🛡️ Security Agent
- Validates command safety
- Sanitizes potentially dangerous operations
- Prevents malicious code generation

### 🧠 Reasoning Agent
- Creates execution plan using Gemini AI
- Breaks down the task into steps
- Shows plan in conversation

### 👨‍💻 Coder Agent
- Generates production-ready code
- Uses the execution plan as guidance
- Considers current file context if available

---

## Tips & Tricks

### 1. Working with Files

- **Open a file** to provide context to the AI
- The AI will see your current file content
- Commands like "add a function" will add to the open file

### 2. Context-Aware Commands

When a file is open:
```
Add a new method called 'calculate_total' to this class
```

The AI knows which file and which class you're referring to.

### 3. Save Your Work

Always save after AI generates code:
- Press `Ctrl+S` or `Cmd+S`
- Or give a voice command: "save this file"

### 4. Resize Panels

Drag the vertical bars between panels to resize them to your preference.

### 5. Clear Chat

Click the trash icon in the Voice Assistant header to clear conversation history.

---

## Architecture

```
Browser (Frontend)
    ↓ WebSocket
Flask Server (Backend)
    ↓
Agent Pipeline:
    1. Speech Agent → STT Tool
    2. Security Agent → Sanitizer
    3. Reasoning Agent → Gemini LLM
    4. Coder Agent → Gemini LLM
    ↓
Generated Code → Sent to Browser → Display in Editor
```

---

## Troubleshooting

### "Failed to load workspace files"
- Check that the server is running
- Verify file permissions in your workspace

### "Agent error: GEMINI_API_KEY not found"
- Make sure `.env` file exists
- Verify `GEMINI_API_KEY` is set correctly
- Restart the server after adding the key

### "Microphone access denied"
- Browser needs microphone permissions
- Click the lock icon in the address bar
- Allow microphone access for localhost

### Code not appearing in editor
- Check the conversation panel for errors
- Verify Gemini API key is valid
- Look at the agent status for which stage failed

### Connection Issues
- Check the status indicator (top right)
- Should show green dot and "Connected"
- If disconnected, refresh the page

---

## Advanced Features

### Custom Workspace

Change the workspace directory:

```bash
python web_ide.py
# Or set WORKSPACE_DIR in code
```

### Agent Logs

All agent interactions are logged:
- Check the conversation panel in the UI
- Server logs in terminal
- Detailed logs in `logs/` directory

### File Operations

- **Read**: Click any file in explorer
- **Write**: Edit and press `Ctrl+S`
- **Create**: Click + button or use voice: "create a new file called test.py"

---

## Next Steps

1. **Try Basic Commands**: Start with simple function creation
2. **Open Existing Files**: Edit your real codebase
3. **Context-Aware Editing**: Use the AI to modify open files
4. **Explore Agent Pipeline**: Watch how agents collaborate
5. **Integrate Voice**: Set up full voice recording with STT

---

## Technology Stack

- **Frontend**: HTML5, CSS3, JavaScript (ES6+)
- **Editor**: Monaco Editor (VS Code engine)
- **Backend**: Flask + Flask-SocketIO
- **AI**: Google Gemini 2.0 Flash
- **Real-time**: WebSocket communication
- **Architecture**: Multi-agent pipeline (ReAct pattern)

---

## Comparison with Traditional IDEs

| Feature | Voice First IDE | Traditional IDE |
|---------|----------------|-----------------|
| Input Method | Voice + Text | Keyboard only |
| AI Integration | Built-in pipeline | Plugin-based |
| Code Generation | Multi-agent system | Copilot-style |
| Real-time Feedback | Agent status visible | Limited |
| Learning Curve | Natural language | Shortcuts/commands |

---

## Contributing

This is a first draft! Areas for improvement:

- [ ] Full voice recording integration
- [ ] File tree drag-and-drop
- [ ] Multiple file tabs
- [ ] Code diff view
- [ ] Terminal integration
- [ ] Git integration
- [ ] Plugin system
- [ ] Collaborative editing

---

## Support

For issues or questions:
1. Check the terminal for error messages
2. Review agent status in the UI
3. Check browser console (F12) for client errors
4. Verify `.env` configuration

---

**🎉 Enjoy coding with your voice!**