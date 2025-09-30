# 🔧 Voice Cursor - Detailed Setup Guide

This guide walks you through setting up Voice Cursor from scratch.

## Prerequisites

Before you begin, ensure you have:

### 1. Python 3.8 or higher

Check your version:
```bash
python --version
# or
python3 --version
```

If you don't have Python installed:
- **macOS**: `brew install python3`
- **Windows**: Download from [python.org](https://www.python.org/downloads/)
- **Linux**: `sudo apt install python3 python3-pip`

### 2. Microphone

Voice Cursor requires a working microphone to capture your speech.

**Testing your microphone:**
```bash
# On macOS/Linux
python3 -c "import speech_recognition as sr; print(sr.Microphone.list_microphone_names())"
```

**Permissions:**
- **macOS**: System Preferences → Security & Privacy → Microphone → Allow Terminal/iTerm
- **Windows**: Settings → Privacy → Microphone → Allow apps to access
- **Linux**: Usually no extra permissions needed

### 3. Internet Connection

Required for:
- Google Speech Recognition (STT)
- Gemini API (code generation)

---

## Installation

### Step 1: Clone the Repository

```bash
# Clone the repo
git clone https://github.com/yourusername/voice-cursor.git
cd voice-cursor
```

### Step 2: Create Virtual Environment (Recommended)

```bash
# Create virtual environment
python3 -m venv venv

# Activate it
# On macOS/Linux:
source venv/bin/activate

# On Windows:
venv\Scripts\activate
```

Your prompt should now show `(venv)` prefix.

### Step 3: Install Dependencies

```bash
pip install -r requirements.txt
```

**What gets installed:**
- `google-generativeai` - Gemini AI
- `SpeechRecognition` - Voice input
- `pyaudio` - Audio processing
- `python-dotenv` - Environment variables
- `rich` - Beautiful console output
- `groq` - Alternative LLM (optional)

**If `pyaudio` fails on macOS:**
```bash
brew install portaudio
pip install pyaudio
```

**If `pyaudio` fails on Linux:**
```bash
sudo apt-get install python3-pyaudio
# or
sudo apt-get install portaudio19-dev
pip install pyaudio
```

**If `pyaudio` fails on Windows:**
```bash
pip install pipwin
pipwin install pyaudio
```

---

## Configuration

### Step 1: Create `.env` file

```bash
cp .env.example .env
```

### Step 2: Get a Gemini API Key

1. Go to [Google AI Studio](https://aistudio.google.com/app/apikey)
2. Sign in with your Google account
3. Click "Create API Key"
4. Copy the key

**Note:** The free tier includes:
- 15 requests per minute
- 1,500 requests per day
- More than enough for testing!

### Step 3: Add API Key to `.env`

Open `.env` in any text editor:

```bash
nano .env
# or
code .env  # if using VS Code
```

Add your key:
```bash
GEMINI_API_KEY=AIzaSy...your-actual-key-here
```

**Complete `.env` example:**
```bash
# Required
GEMINI_API_KEY=AIzaSy...your-key

# Optional (defaults shown)
LLM_PROVIDER=gemini
LLM_MODEL=gemini-2.0-flash-exp
STT_PROVIDER=google
ENABLE_SANITIZER=true
AUTO_FORMAT=true
```

Save and close the file.

---

## Verification

### Test Your Setup

```bash
python test_3_agents.py
```

Expected flow:
1. Script starts
2. Prompts you to press Enter
3. Says "🔴 Recording... Speak now!"
4. You speak (e.g., "create a hello world function")
5. Processing (~5-10 seconds)
6. Code generated and saved to `output_test/`

### Check Generated Code

```bash
ls -la output_test/
cat output_test/*.py
```

### View Logs

```bash
# View latest log
cat logs/agent_calls_*.log

# Or use the log viewer
python view_logs.py
```

---

## Project Structure

```
voice-cursor/
├── agents/                      # AI Agents
│   ├── speech_agent.py         # Voice → Text
│   ├── security_agent.py       # Input validation
│   ├── reasoning_agent.py      # Planning
│   ├── coder_agent.py          # Code generation
│   └── validator_agent.py      # Code review
│
├── tools/                       # API Wrappers
│   ├── stt_tool.py             # Speech-to-Text
│   ├── llm_tool.py             # Gemini API
│   └── sanitizer_tool.py       # Security checks
│
├── utils/                       # Utilities
│   └── logger.py               # Logging system
│
├── config/                      # Configuration
│   └── settings.py             # Settings loader
│
├── output_test/                 # Generated code saves here
├── logs/                        # Agent logs
├── test_3_agents.py            # Main entry point
├── main.py                      # Alternative entry point
├── .env                         # Your API keys (never commit!)
└── requirements.txt             # Dependencies
```

---

## Usage

### Basic Usage

```bash
python test_3_agents.py
```

1. Press Enter when ready
2. Speak clearly: "Create a function to [do something]"
3. Wait for processing
4. Find code in `output_test/`

### Example Commands

**Good commands:**
- ✅ "Create a function to calculate factorial"
- ✅ "Write a class to manage a shopping cart"
- ✅ "Build a REST API endpoint for user login"
- ✅ "Generate a script to parse CSV files"

**Too vague:**
- ❌ "Write some code"
- ❌ "Make a program"

**Be specific about:**
- What you want (function, class, script)
- What it should do
- Any special requirements

---

## Troubleshooting

### Issue: "GEMINI_API_KEY not found"

**Solution:**
```bash
# Check .env exists
ls -la .env

# Check it has the key
cat .env | grep GEMINI_API_KEY

# If missing, add it:
echo "GEMINI_API_KEY=your_key_here" >> .env
```

### Issue: "No module named 'speech_recognition'"

**Solution:**
```bash
pip install -r requirements.txt

# If still fails, try:
pip install --upgrade pip
pip install -r requirements.txt --force-reinstall
```

### Issue: Microphone not detected

**macOS:**
```bash
# Check permissions
System Preferences → Security & Privacy → Microphone

# Test in Python
python3 -c "import speech_recognition as sr; print(sr.Microphone.list_microphone_names())"
```

**Linux:**
```bash
# Install ALSA
sudo apt-get install libasound-dev portaudio19-dev

# Test recording
arecord -d 3 test.wav
aplay test.wav
```

### Issue: "Could not understand audio"

**Solutions:**
- Speak more clearly and slowly
- Reduce background noise
- Move closer to microphone
- Check microphone is not muted
- Try: `python -c "import speech_recognition as sr; r = sr.Recognizer(); print(r.energy_threshold)"`

### Issue: Rate limit errors from Gemini

**Solution:**
- Free tier: 15 requests/min
- Wait a minute between tests
- Or upgrade to paid tier

### Issue: Import errors with pyaudio

**macOS:**
```bash
brew install portaudio
pip uninstall pyaudio
pip install --no-cache-dir pyaudio
```

**Windows:**
```bash
pip install pipwin
pipwin install pyaudio
```

**Linux:**
```bash
sudo apt-get install python3-pyaudio
# or
sudo apt-get install portaudio19-dev python3-dev
pip install pyaudio
```

---

## Advanced Configuration

### Using Different LLM Models

Edit `.env`:
```bash
# Use Gemini Pro
LLM_MODEL=gemini-1.5-pro

# Use Gemini Flash (faster, cheaper)
LLM_MODEL=gemini-2.0-flash-exp
```

### Adjusting Voice Recognition

Edit `test_3_agents.py` line 62-64:
```python
recognizer.energy_threshold = 300      # Lower = more sensitive
recognizer.pause_threshold = 1.5       # Seconds of silence
```

### Custom Output Directory

Edit `test_3_agents.py` line 41:
```python
OUTPUT_DIR = Path("my_custom_output")
```

### Logging Verbosity

Edit `utils/logger.py` or set:
```bash
export LOG_LEVEL=DEBUG
```

---

## Architecture Overview

Voice Cursor uses a **multi-agent architecture**:

1. **Speech Agent** 🎤
   - Captures microphone input
   - Uses Google Speech Recognition
   - Returns transcript

2. **Security Agent** 🛡️
   - Validates command safety
   - Blocks malicious requests
   - Sanitizes input

3. **Reasoning Agent** 🧠
   - Creates execution plan
   - Breaks down complex tasks
   - Uses Gemini AI

4. **Coder Agent** 👨‍💻
   - Generates actual code
   - Follows plan from Reasoning Agent
   - Produces clean, working code

5. **Validator Agent** ✅ (optional)
   - Reviews generated code
   - Can run tests
   - Applies to files

Each agent:
- Has single responsibility
- Uses tools (APIs) to do work
- Returns structured results
- Logs all actions

---

## Development

### Running Tests

```bash
# Run main test suite
python test_3_agents.py

# View logs
python view_logs.py

# Check specific agent
python -c "from agents.speech_agent import SpeechAgent; print('OK')"
```

### Code Structure

Each agent inherits from `BaseAgent`:
```python
class MyAgent(BaseAgent):
    def execute(self, input_data, context=None):
        # Do work
        return AgentResult(success=True, data=result)
```

Each tool inherits from `BaseTool`:
```python
class MyTool(BaseTool):
    def execute(self, **kwargs):
        # Call external API
        return result
```

---

## Getting Help

1. **Check the logs**: `cat logs/agent_calls_*.log`
2. **Read error messages carefully**
3. **Search this document** for your error
4. **Check your `.env` file** has correct keys
5. **Verify internet connection**
6. **Test microphone separately**

---

## Next Steps

Once setup is complete:

1. ✅ Run `python test_3_agents.py`
2. ✅ Try the example commands
3. ✅ Experiment with different prompts
4. ✅ Check `output_test/` for generated code
5. ✅ Review `logs/` to see agent activity

**Have fun coding with your voice!** 🎙️✨