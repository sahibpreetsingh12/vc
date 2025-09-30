# 👋 Welcome to Voice Cursor!

**New here?** Follow this checklist to get started in 5 minutes.

## ✅ Setup Checklist

### 1️⃣ Clone Repository
```bash
git clone <your-repo-url>
cd voice-cursor
```

### 2️⃣ Install Python Dependencies
```bash
pip install -r requirements.txt
```

**Note:** If `pyaudio` fails, see [SETUP.md](SETUP.md#step-3-install-dependencies) for platform-specific fixes.

### 3️⃣ Get Gemini API Key (Free)
1. Visit: https://aistudio.google.com/app/apikey
2. Sign in with Google account
3. Click "Create API Key"
4. Copy the key

### 4️⃣ Configure Environment
```bash
# Copy example file
cp .env.example .env

# Edit .env and add your key
nano .env  # or use your favorite editor
```

Add this line:
```
GEMINI_API_KEY=your_actual_key_here
```

Save and close.

### 5️⃣ Test Your Setup
```bash
python test_3_agents.py
```

**Expected:**
- Prompt asks you to press Enter ✅
- Says "Recording... Speak now!" ✅
- You speak: "create a hello world function" ✅
- Processing happens (~10 seconds) ✅
- Code saves to `output_test/` ✅
- Logs save to `logs/` ✅

### 6️⃣ Check Output
```bash
# See generated code
ls output_test/
cat output_test/*.py

# View logs
cat logs/agent_calls_*.log
```

---

## 🎯 What to Try Next

### Example Commands
Say these clearly into your microphone:

1. **"Create a function to calculate factorial"**
   - Generates recursive or iterative factorial function

2. **"Write a class to manage a todo list"**
   - Creates a TodoList class with add/remove/list methods

3. **"Build an API endpoint to fetch user data"**
   - Generates Flask/FastAPI endpoint skeleton

4. **"Generate a script to parse CSV files"**
   - Creates CSV reading and processing code

### Tips for Best Results
- ✅ **Speak clearly** and at normal pace
- ✅ **Be specific** about what you want
- ✅ **Use action verbs**: "create", "write", "build", "generate"
- ✅ **Mention type**: "function", "class", "script", "API"
- ❌ **Avoid vague**: "make some code", "do something"

---

## 📚 Documentation Guide

Depending on your needs:

| If you want... | Read this |
|----------------|-----------|
| **Quick 3-step setup** | [QUICKSTART.md](QUICKSTART.md) |
| **Full installation guide** | [SETUP.md](SETUP.md) |
| **Overview & examples** | [README.md](README.md) |
| **This checklist** | You're here! 👋 |

---

## 🔧 Common Issues

### "GEMINI_API_KEY not found"
- Did you create `.env`? Run: `cp .env.example .env`
- Did you add your key to `.env`?
- Is the key valid? Test at: https://aistudio.google.com/

### "No module named 'speech_recognition'"
```bash
pip install -r requirements.txt
```

### "Microphone not detected"
- **macOS**: System Preferences → Security & Privacy → Microphone
- **Linux**: Check `arecord -l` shows devices
- **Windows**: Settings → Privacy → Microphone

### "Could not understand audio"
- Reduce background noise
- Speak more clearly
- Move closer to mic
- Check mic isn't muted

### More help?
See full troubleshooting in [SETUP.md](SETUP.md#troubleshooting)

---

## 🎙️ How Voice Cursor Works

```
1. You speak → 2. STT converts → 3. Security validates
         ↓
4. AI plans → 5. AI codes → 6. Saves to file
```

**Behind the scenes:**
- **Speech Agent**: Google STT (free)
- **Security Agent**: Blocks malicious requests
- **Reasoning Agent**: Gemini AI plans implementation
- **Coder Agent**: Gemini AI generates code
- **Logger**: Tracks everything for debugging

---

## ✨ Success Indicators

You're all set when:
- ✅ `python test_3_agents.py` runs without errors
- ✅ You can speak and see "✓ Heard: ..." message
- ✅ Code appears in `output_test/` folder
- ✅ Logs appear in `logs/` folder
- ✅ Generated code is syntactically correct

---

## 🚀 Next Steps

Once you're comfortable:

1. **Experiment** with different commands
2. **Check logs** to see how agents work
3. **Modify prompts** for better results
4. **Share your creations** on social media!
5. **Read SETUP.md** for advanced configuration

---

## 🤝 Need Help?

1. Check [SETUP.md](SETUP.md) troubleshooting section
2. Review `logs/agent_calls_*.log` for errors
3. Verify `.env` has correct API key
4. Test microphone with: `python -c "import speech_recognition as sr; print(sr.Microphone.list_microphone_names())"`

---

## 🎊 That's It!

You're ready to code with your voice! 

**Start with:** `python test_3_agents.py`

**Say:** "Create a function to [what you need]"

**Get:** Working code in seconds!

---

*Happy voice coding!* 🎙️✨