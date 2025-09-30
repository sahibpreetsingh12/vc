# 🤖 AI Models Configuration

## Current Setup (Updated)

### 1. **LLM Models - Gemini 2.5 Flash Latest** 🚀

#### Reasoning Agent
- **Model**: `gemini-2.5-flash-latest`
- **Provider**: Google Gemini
- **Purpose**: Creates execution plans and breaks down tasks into steps
- **Why**: Latest model with improved reasoning capabilities

#### Coder Agent
- **Model**: `gemini-2.5-flash-latest`
- **Provider**: Google Gemini  
- **Purpose**: Generates production-ready code based on execution plan
- **Why**: Latest model for best code generation quality

**Features:**
- ✅ Fastest Gemini model
- ✅ Latest version with improved capabilities
- ✅ Better context understanding
- ✅ More accurate code generation
- ✅ Supports longer context windows

---

### 2. **Speech-to-Text - Hybrid Approach** 🎤

#### Primary: Web Speech API (Google)
- **Provider**: Google Speech Recognition (Browser-based)
- **Model**: Chrome's built-in speech recognition
- **Latency**: ~200ms (Real-time)
- **Accuracy**: High (consumer-grade)
- **Cost**: Free
- **Benefits**: 
  - ✅ Instant transcription
  - ✅ No backend processing needed
  - ✅ Works offline in some browsers
  - ✅ Low latency
  - ✅ Good UX

#### Backend: Google Cloud Speech-to-Text (SOTA)
- **Provider**: Google Cloud Platform
- **Model**: `latest_long` with enhanced model
- **Latency**: ~1-2s (depending on audio length)
- **Accuracy**: SOTA (State-of-the-art)
- **Cost**: Pay-per-use
- **Configuration**:
  ```python
  model='latest_long'
  use_enhanced=True  # Best accuracy
  enable_automatic_punctuation=True
  ```

**Why Hybrid?**
- Frontend uses Web Speech API for instant feedback
- Backend validates with Google Cloud STT for critical tasks
- Best of both worlds: Speed + Accuracy

---

## Configuration Files

### `.env`
```bash
LLM_PROVIDER=gemini
LLM_MODEL=gemini-2.5-flash-latest
STT_PROVIDER=google
GEMINI_API_KEY=your_key_here
GOOGLE_APPLICATION_CREDENTIALS=/path/to/credentials.json
```

### `config/settings.py`
```python
LLM_PROVIDER: str = os.getenv("LLM_PROVIDER", "gemini")
LLM_MODEL: str = os.getenv("LLM_MODEL", "gemini-2.5-flash-latest")
```

### `tools/llm_tool.py`
```python
def __init__(self, model: str = "gemini-2.5-flash-latest"):
    # Uses latest Gemini model
```

### `tools/stt_tool.py`
```python
config = speech.RecognitionConfig(
    model='latest_long',
    use_enhanced=True,  # SOTA model
)
```

---

## Model Comparison

### Gemini 2.5 Flash vs 2.0 Flash

| Feature | 2.0 Flash | 2.5 Flash Latest |
|---------|-----------|------------------|
| Speed | Fast | Faster |
| Reasoning | Good | Better |
| Code Quality | Good | Excellent |
| Context Window | 1M tokens | 2M tokens |
| Cost | Low | Similar |
| Release | Nov 2024 | Dec 2024 |

### STT Comparison

| Provider | Latency | Accuracy | Cost | Use Case |
|----------|---------|----------|------|----------|
| Web Speech API | ~200ms | High | Free | Real-time UI |
| Google Cloud STT | ~1-2s | SOTA | $0.006/15s | Critical tasks |
| Groq Whisper | ~500ms | High | Free tier | Alternative |

---

## Performance Characteristics

### Reasoning Agent (Gemini 2.5 Flash)
- **Input**: User command + context
- **Output**: Execution plan with steps
- **Average Time**: 1-2 seconds
- **Token Limit**: 2M context, 8k output

### Coder Agent (Gemini 2.5 Flash)
- **Input**: Execution plan + existing code
- **Output**: Production-ready code
- **Average Time**: 2-4 seconds
- **Token Limit**: 2M context, 8k output

### Speech Agent (Hybrid)
- **Web API**: 0.2-0.5 seconds (real-time)
- **Google Cloud**: 1-2 seconds (when used)
- **Accuracy**: >95% for clear speech

---

## Cost Estimation

### Gemini 2.5 Flash
- **Input**: $0.075 per 1M tokens
- **Output**: $0.30 per 1M tokens
- **Typical Request**: ~$0.001-0.005
- **100 requests**: ~$0.10-0.50

### Google Cloud STT (if used)
- **Price**: $0.006 per 15 seconds
- **Typical Request**: ~$0.006
- **100 requests**: ~$0.60

**Total**: Very affordable for development and production use!

---

## How to Switch Models

### Use Groq Instead (Faster, Free Tier)
```bash
echo "LLM_PROVIDER=groq" >> .env
echo "LLM_MODEL=llama-3.3-70b-versatile" >> .env
```

### Use Gemini Pro (More Powerful)
```bash
echo "LLM_MODEL=gemini-1.5-pro-latest" >> .env
```

### Force Google Cloud STT Only
Remove Web Speech API handling in `static/js/app.js` and send audio directly to backend.

---

## Monitoring

### Check Current Configuration
```python
from config import settings
print(f"LLM: {settings.LLM_PROVIDER} - {settings.LLM_MODEL}")
print(f"STT: {settings.STT_PROVIDER}")
```

### View Logs
```bash
# Agent logs
cat logs/*.log

# View in UI
python view_logs.py
```

---

## Troubleshooting

### Gemini API Errors
```bash
# Check API key
echo $GEMINI_API_KEY

# Test API
python -c "import google.generativeai as genai; genai.configure(api_key='your_key'); print('OK')"
```

### Google Cloud STT Errors
```bash
# Check credentials
echo $GOOGLE_APPLICATION_CREDENTIALS
cat $GOOGLE_APPLICATION_CREDENTIALS

# Test STT
python -c "from google.cloud import speech; client = speech.SpeechClient(); print('OK')"
```

### Web Speech API Not Working
- **Chrome**: Check microphone permissions (chrome://settings/content/microphone)
- **Safari**: Allow microphone in System Preferences
- **Edge**: Similar to Chrome

---

## Best Practices

1. **Development**: Use Web Speech API for fast iteration
2. **Production**: Add Google Cloud STT validation for critical tasks
3. **Cost Optimization**: Cache common requests
4. **Monitoring**: Log confidence scores to track quality
5. **Fallbacks**: Always have text input as backup

---

## Future Enhancements

- [ ] Add streaming STT for long audio
- [ ] Implement Whisper for offline mode
- [ ] Add multi-language support
- [ ] Fine-tune models on coding tasks
- [ ] Add voice activity detection
- [ ] Implement noise cancellation

---

**Last Updated**: 2025-09-30
**Gemini Version**: 2.5 Flash Latest
**STT**: Hybrid (Web API + Google Cloud)