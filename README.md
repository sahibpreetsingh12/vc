# 🎙️ Voice Cursor

**Speak your code into existence.** A multi-agent voice-to-code system powered by AI.

## What is this?

Voice Cursor lets you speak naturally to generate working code. Say "create a function to calculate fibonacci numbers" and watch as AI:
1. 🎤 Transcribes your speech
2. 🛡️ Validates the request is safe
3. 🧠 Plans the implementation
4. 👨‍💻 Generates production-ready code
5. 💾 Saves it to a file

---

**👋 First time here?** Check out the [New User Guide](NEW_USER_GUIDE.md) for a step-by-step checklist!

---

## Quick Start (3 steps)

### 1. Clone & Install

```bash
git clone <your-repo-url>
cd voice-cursor
pip install -r requirements.txt
```

### 2. Set Up API Keys

```bash
# Copy the example environment file
cp .env.example .env

# Edit .env and add your Gemini API key
# Get one free at: https://aistudio.google.com/app/apikey
```

**Required in `.env`:**
```bash
GEMINI_API_KEY=your_key_here
```

### 3. Run!

```bash
python test_3_agents.py
```

Then:
- Press Enter when prompted
- Speak your coding request clearly
- Wait ~10 seconds for AI to generate code
- Find your code in `output_test/`

## Examples

Try saying:
- "Create a function to validate email addresses"
- "Write a class to manage a todo list"
- "Build an API endpoint to fetch user data"
- "Generate a script to rename files in a directory"

## How It Works

```
    🎤 You Speak
      ↓
[Speech Agent] → Google STT
      ↓
[Security Agent] → Validates safety
      ↓
[Reasoning Agent] → Plans with Gemini AI
      ↓
[Coder Agent] → Generates code with Gemini
      ↓
    💾 Saved to file
```

## Project Structure

```
voice-cursor/
├── agents/              # AI agents (Speech, Security, Reasoning, Coder)
├── tools/               # API wrappers (STT, LLM, Sanitizer)
├── utils/               # Logging utilities
├── config/              # Settings
├── output_test/         # Generated code goes here
├── logs/                # Agent logs
├── test_3_agents.py     # Main entry point
└── requirements.txt     # Dependencies
```

## Requirements

- Python 3.8+
- Microphone (for voice input)
- Internet connection
- Gemini API key (free tier works)

## Troubleshooting

**"No module named 'speech_recognition'"**
```bash
pip install -r requirements.txt
```

**"GEMINI_API_KEY not found"**
- Make sure you created `.env` from `.env.example`
- Add your API key to `.env`

**"Microphone not working"**
- Check system permissions for microphone access
- Try running: `python -c "import speech_recognition as sr; print(sr.Microphone.list_microphone_names())"`

**"Could not understand audio"**
- Speak more clearly
- Check background noise levels
- Try moving closer to the microphone

## Advanced

For detailed setup instructions, see [SETUP.md](SETUP.md)

---

**Built with:** Google Gemini AI, SpeechRecognition, Rich Console
