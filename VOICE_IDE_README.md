# 🎙️ Voice First IDE

<p align="center">
  <img src="https://img.shields.io/badge/Python-3.8+-blue.svg" alt="Python">
  <img src="https://img.shields.io/badge/Flask-3.0-green.svg" alt="Flask">
  <img src="https://img.shields.io/badge/Gemini-2.0-orange.svg" alt="Gemini">
  <img src="https://img.shields.io/badge/License-MIT-yellow.svg" alt="License">
</p>

**Develop code with your voice.** A VS Code-like IDE powered by AI agents that understands natural language commands.

![Voice First IDE](https://via.placeholder.com/800x400?text=Voice+First+IDE+Screenshot)

---

## ✨ Features

### 🎨 VS Code-Like Interface
- **Three-panel layout**: File explorer | Code editor | Voice assistant
- **Monaco Editor**: Full VS Code editing experience with syntax highlighting
- **Resizable panels**: Drag to adjust panel sizes
- **File operations**: Browse, open, edit, save files

### 🎤 Voice-First Development
- **Natural language commands**: "Create a function to calculate fibonacci"
- **Context-aware**: Works with your open files
- **Real-time transcription**: See your commands as you speak
- **Text input fallback**: Type commands when voice isn't available

### 🤖 Multi-Agent AI Pipeline
1. **🎤 Speech Agent**: Converts voice to text
2. **🛡️ Security Agent**: Validates command safety
3. **🧠 Reasoning Agent**: Plans execution steps
4. **👨‍💻 Coder Agent**: Generates production code

### ⚡ Real-Time Updates
- **Live agent status**: See each agent working
- **WebSocket communication**: Instant feedback
- **Conversation history**: Track all interactions
- **Progress indicators**: Visual pipeline status

---

## 🚀 Quick Start

### 1️⃣ Install Dependencies

```bash
pip install -r requirements.txt
```

### 2️⃣ Set Up API Key

```bash
# Create .env file
echo "GEMINI_API_KEY=your_key_here" > .env
```

Get your free Gemini API key: https://aistudio.google.com/app/apikey

### 3️⃣ Run the IDE

```bash
python web_ide.py
```

### 4️⃣ Open Browser

Navigate to: **http://localhost:5000**

---

## 📖 Usage

### Type a Command (Easiest Way to Start)

1. In the right panel, type in the text box:
   ```
   Create a function to calculate fibonacci numbers
   ```

2. Press **Enter** or click **Send**

3. Watch the AI agents work their magic! 🪄

### Use Voice Input

1. Click the **🎤 microphone button**
2. Speak your command clearly
3. Click again to stop
4. AI processes and generates code

### Example Commands

```
✅ Create a REST API endpoint to fetch users
✅ Add error handling to the calculate function
✅ Write a class for managing a shopping cart
✅ Refactor this code to use async/await
✅ Add unit tests for the UserService class
```

---

## 🏗️ Architecture

```
┌─────────────────────────────────────────────────────┐
│                   Browser (UI)                      │
│  ┌─────────┐  ┌──────────┐  ┌──────────────────┐  │
│  │  Files  │  │  Editor  │  │  Voice Chat      │  │
│  │ Explorer│  │ (Monaco) │  │  + Agent Status  │  │
│  └─────────┘  └──────────┘  └──────────────────┘  │
└──────────────────┬──────────────────────────────────┘
                   │ WebSocket
┌──────────────────▼──────────────────────────────────┐
│            Flask Server (web_ide.py)                │
│  ┌─────────────────────────────────────────────┐   │
│  │         Agent Pipeline                      │   │
│  │  Speech → Security → Reasoning → Coder     │   │
│  └─────────────────────────────────────────────┘   │
└──────────────────┬──────────────────────────────────┘
                   │
┌──────────────────▼──────────────────────────────────┐
│              External Services                      │
│  • Google Gemini 2.0 (LLM)                         │
│  • Speech Recognition API (optional)               │
└─────────────────────────────────────────────────────┘
```

---

## 📂 Project Structure

```
voice-cursor/
├── web_ide.py              # Flask web server (main entry point)
├── templates/
│   └── index.html          # Main UI template
├── static/
│   ├── css/
│   │   └── style.css       # VS Code-like styling
│   └── js/
│       └── app.js          # Frontend application logic
├── agents/                 # AI agent implementations
│   ├── speech_agent.py     # Voice to text
│   ├── security_agent.py   # Command validation
│   ├── reasoning_agent.py  # Plan generation
│   └── coder_agent.py      # Code generation
├── tools/                  # Agent tools
│   ├── stt_tool.py         # Speech-to-text
│   ├── llm_tool.py         # Gemini integration
│   └── sanitizer_tool.py   # Security checks
├── config/
│   └── settings.py         # Configuration
├── utils/
│   └── logger.py           # Logging utilities
├── requirements.txt        # Python dependencies
└── VOICE_IDE_GUIDE.md     # Detailed documentation
```

---

## 🎯 How It Works

### Step-by-Step Flow

1. **User Input**: Type or speak a command
   ```
   "Create a function to validate emails"
   ```

2. **Speech Agent** (if voice):
   - Transcribes audio to text
   - Displays transcript in UI

3. **Security Agent**:
   - Validates command safety
   - Prevents malicious operations
   - Sanitizes input

4. **Reasoning Agent**:
   - Analyzes the command
   - Creates execution plan with steps
   - Uses Gemini AI for planning

5. **Coder Agent**:
   - Generates production-ready code
   - Follows the execution plan
   - Considers file context (if file open)
   - Uses Gemini AI for generation

6. **Result**:
   - Code displayed in conversation
   - Option to insert into editor
   - Save to file

---

## 🔧 Configuration

### Environment Variables

Create a `.env` file:

```bash
# Required
GEMINI_API_KEY=your_gemini_api_key

# Optional
LLM_PROVIDER=gemini
LLM_MODEL=gemini-2.0-flash-exp
ENABLE_SANITIZER=true
AUTO_FORMAT=true
```

### Change Workspace Directory

Edit `web_ide.py`:

```python
WORKSPACE_DIR = Path("/path/to/your/project")
```

---

## 🌟 Key Features Explained

### Monaco Editor Integration

Same editor engine as VS Code:
- Syntax highlighting for 50+ languages
- IntelliSense and autocomplete
- Keyboard shortcuts (Ctrl+S to save)
- Minimap for navigation

### Real-Time Agent Status

Watch each agent as it works:
- `idle` → `processing` → `completed` → `idle`
- Visual indicators in the UI
- Error states displayed clearly

### Context-Aware Code Generation

When you have a file open:
- AI sees the current file content
- Understands the codebase context
- Can modify or extend existing code
- Preserves your code style

### Security First

The Security Agent prevents:
- File system manipulation
- Network requests
- Dangerous system calls
- Code injection attempts

---

## 🎨 UI Highlights

### Dark Theme (VS Code Style)
- Professional developer aesthetic
- Easy on the eyes for long coding sessions
- Syntax highlighting with Monaco

### Responsive Layout
- Resizable panels
- Works on desktop browsers
- Optimized for 1080p and above

### Real-Time Feedback
- Live agent status updates
- Conversation history
- Code preview in chat
- Error messages with context

---

## 🔮 Future Enhancements

### Planned Features
- [ ] Full voice recording with STT integration
- [ ] Multiple file tabs
- [ ] Terminal integration
- [ ] Git integration
- [ ] Code diff viewer
- [ ] Collaborative editing
- [ ] Plugin system
- [ ] Custom agent workflows
- [ ] Code review agent
- [ ] Testing agent

---

## 💡 Use Cases

### 1. Rapid Prototyping
Speak your ideas and watch code materialize:
```
"Create a simple HTTP server with two endpoints"
```

### 2. Learning & Education
Natural language queries help students learn:
```
"Explain how this function works and add comments"
```

### 3. Accessibility
Voice-first interface for developers with mobility challenges

### 4. Hands-Free Coding
Code while cooking, exercising, or away from keyboard

### 5. Pair Programming with AI
Collaborate with AI agents instead of just using autocomplete

---

## 🤝 Contributing

Contributions welcome! This is a first draft with room for improvement.

### Areas We Need Help With
- Voice recording/STT integration
- Additional language support
- Performance optimization
- Mobile responsiveness
- Agent capabilities expansion

---

## 📝 License

MIT License - feel free to use this in your projects!

---

## 🙏 Acknowledgments

- **Monaco Editor** - Microsoft's excellent editor
- **Google Gemini** - Powerful AI for planning and coding
- **Flask & SocketIO** - Real-time web framework
- **VS Code** - Interface inspiration

---

## 📞 Support

Having issues? Check the guide:
- Read [VOICE_IDE_GUIDE.md](VOICE_IDE_GUIDE.md) for detailed docs
- Check terminal logs for errors
- Review agent status in UI
- Verify `.env` configuration

---

## 🎉 Get Started Now!

```bash
# Clone the repo (if not already)
cd voice-cursor

# Install dependencies
pip install -r requirements.txt

# Add your API key
echo "GEMINI_API_KEY=your_key" > .env

# Run the IDE
python web_ide.py

# Open browser
# → http://localhost:5000
```

**Start coding with your voice today!** 🎤💻✨