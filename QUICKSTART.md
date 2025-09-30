# ⚡ Voice Cursor - Quick Start (5 Minutes)

Get up and running in 3 commands.

## Prerequisites
- Python 3.8+
- Microphone
- Internet connection

## Installation

```bash
# 1. Clone and enter directory
git clone <your-repo-url>
cd voice-cursor

# 2. Install dependencies
pip install -r requirements.txt

# 3. Set up API key
cp .env.example .env
# Edit .env and add: GEMINI_API_KEY=your_key_here
```

**Get Gemini API Key (free):** https://aistudio.google.com/app/apikey

## Run It

```bash
python test_3_agents.py
```

1. Press Enter when ready
2. Speak: "Create a function to calculate factorial"
3. Wait 10 seconds
4. Check `output_test/` for generated code

## Examples

Try saying:
- "Create a function to validate email addresses"
- "Write a class for a todo list"
- "Build an API endpoint to fetch user data"

## Need Help?

- **Full guide:** See [SETUP.md](SETUP.md)
- **Can't hear you:** Check microphone permissions
- **API errors:** Verify GEMINI_API_KEY in `.env`
- **Python errors:** Run `pip install -r requirements.txt`

---

**That's it!** Start coding with your voice 🎙️