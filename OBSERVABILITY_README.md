# Observability Features - Voice First IDE

## Overview
Complete observability system has been added to track and analyze all agent pipeline executions in real-time.

## Features Implemented

### 1. **Observability Tracker** (`utils/observability.py`)
A comprehensive tracking system that captures:
- **Agents Used**: Tracks which agents (Speech, Security, Reasoning, Coder) are invoked
- **Query/Command**: Records the user's original input
- **Tools Used**: Tracks all tools in execution order (STT, LLM, Sanitizer, etc.)
- **Token Count**: Monitors token usage per tool/agent
- **Cost Calculation**: Calculates cost based on provider pricing
  - Gemini 2.0 Flash: Free tier
  - Groq Llama 3.3: $0.59/$0.79 per 1M tokens (input/output)
  - Google Cloud STT: $0.009 per minute
  - Web Speech API: Free
- **Step-wise Latency**: Measures execution time for each agent and tool

### 2. **Observability Dashboard** (`/observability` route)
A modern, real-time dashboard featuring:

#### Summary Statistics Cards
- Total Requests
- Successful Requests
- Total Tokens Used
- Total Cost (USD)
- Average Latency
- Unique Agents Used

#### Request History Table
- Timestamp
- Query/Command
- Agents Used (badges)
- Tools Used (badges)
- Token Count
- Cost per request
- Latency
- Status (Success/Failed)
- View Details button

#### Detailed View Modal
For each request, view:
- **Overview**: Query, Status, Timestamp
- **Metrics**: Tokens, Cost, Latency, Agents count
- **Agent Timeline**: Step-by-step execution with latency per agent
- **Tool Usage**: Execution order with input/output sizes
- **Error Details**: If applicable

#### Interactive Features
- **Search**: Filter requests by query text
- **Status Filter**: Show all, successful only, or failed only
- **Auto-refresh**: Updates every 30 seconds
- **Responsive Design**: Works on desktop and mobile

### 3. **Integration**
The observability tracking is seamlessly integrated into the voice command pipeline:
- Automatic tracking starts when a voice command is received
- Each agent execution is tracked with timing
- Each tool usage is logged with token counts
- Success/failure status is captured
- Data persists to disk in `logs/observability/` directory

### 4. **UI Enhancement**
Added a modern "Observability" button in the main IDE header:
- Gradient purple design matching the dashboard theme
- Opens in new tab
- Easy access to metrics

## File Structure

```
voice-cursor/
├── utils/
│   └── observability.py          # Core tracking logic
├── templates/
│   └── observability.html         # Dashboard HTML
├── static/
│   ├── css/
│   │   └── observability.css      # Dashboard styles
│   └── js/
│       └── observability.js       # Dashboard JavaScript
├── logs/
│   └── observability/             # Stored metrics (auto-created)
│       └── *.json                 # Individual request records
└── web_ide.py                     # Integrated tracking

```

## Usage

### Accessing the Dashboard
1. Start the Flask app: `python3 web_ide.py`
2. Open the main IDE: `http://localhost:8081`
3. Click the **"Observability"** button in the top-right header
4. Dashboard opens in a new tab

### API Endpoints
- `GET /observability` - Serve the dashboard page
- `GET /api/observability/data` - Get JSON data of all records and summary stats

### Data Persistence
- Records are automatically saved to `logs/observability/` as JSON files
- Filename format: `YYYYMMDD_HHMMSS_microseconds.json`
- Last 100 records are loaded on dashboard startup
- Data persists across server restarts

## Pricing Configuration

Update pricing in `utils/observability.py` if needed:

```python
PRICING = {
    "gemini-2.0-flash-exp": {
        "input": 0.00,  # Free tier
        "output": 0.00
    },
    "llama-3.3-70b-versatile": {
        "input": 0.59,  # per 1M tokens
        "output": 0.79
    },
    "google_stt_enhanced": {
        "per_minute": 0.009
    },
    "web_speech_api": {
        "per_minute": 0.00  # Free
    }
}
```

## Benefits

1. **Cost Monitoring**: Track spending on API calls
2. **Performance Analysis**: Identify slow agents/tools
3. **Debugging**: View full execution timeline for failed requests
4. **Usage Patterns**: Understand how users interact with the system
5. **Optimization**: Find bottlenecks in the pipeline
6. **Accountability**: Complete audit trail of all operations

## Technical Details

### Tracking Flow
1. User submits voice command
2. `tracker.start_tracking(query)` initializes tracking
3. Each agent start/end is tracked with `track_agent_start/end()`
4. Each tool usage is tracked with `track_tool_usage()`
5. `tracker.end_tracking(success, error)` saves the record

### Token Estimation
- Rough approximation: 1 token ≈ 4 characters
- More accurate counts can be obtained from LLM provider responses
- Customize in your tool implementations

### Latency Measurement
- Uses Python's `time.time()` for precise timing
- Measured in milliseconds
- Captures total pipeline latency and per-agent latency

---

**Note**: The observability system is production-ready but can be extended with:
- Export to CSV/Excel
- Integration with monitoring tools (Grafana, Prometheus)
- Alerting on errors or cost thresholds
- Historical trend analysis
- User-specific tracking
