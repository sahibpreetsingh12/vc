#!/usr/bin/env python3
"""
Voice First IDE - Web Server
A VS Code-like interface with voice-first development capabilities
"""

from flask import Flask, render_template, request, jsonify, send_from_directory
from flask_socketio import SocketIO, emit
from pathlib import Path
import os
import json
import threading
import base64
import io
import wave

# Import agents
from agents.speech_agent import SpeechAgent
from agents.security_agent import SecurityAgent
from agents.reasoning_agent import ReasoningAgent
from agents.coder_agent import CoderAgent

# Import tools
from tools.stt_tool import create_stt_tool
from tools.sanitizer_tool import SanitizerTool
from tools.llm_tool import GeminiLLMTool

# Import logging
from utils.logger import get_logger, reset_logger

# Import observability
from utils.observability import get_tracker

app = Flask(__name__)
app.config['SECRET_KEY'] = 'voice-cursor-ide-secret'
socketio = SocketIO(app, cors_allowed_origins="*")

# Global workspace directory (user can change this)
WORKSPACE_DIR = Path.cwd()


def get_file_tree(directory: Path, max_depth=5, current_depth=0):
    """Get file tree structure for the file explorer."""
    if current_depth >= max_depth:
        return []
    
    try:
        items = []
        for item in sorted(directory.iterdir()):
            # Skip hidden files and common ignore patterns
            if item.name.startswith('.') or item.name in ['__pycache__', 'node_modules', 'venv', '.git']:
                continue
            
            if item.is_dir():
                items.append({
                    'name': item.name,
                    'type': 'directory',
                    'path': str(item.relative_to(WORKSPACE_DIR)),
                    'children': get_file_tree(item, max_depth, current_depth + 1)
                })
            else:
                items.append({
                    'name': item.name,
                    'type': 'file',
                    'path': str(item.relative_to(WORKSPACE_DIR)),
                    'size': item.stat().st_size
                })
        
        return items
    except PermissionError:
        return []


@app.route('/')
def index():
    """Serve the main IDE interface."""
    return render_template('index.html')


@app.route('/api/workspace/files')
def get_files():
    """Get the file tree structure."""
    try:
        tree = get_file_tree(WORKSPACE_DIR)
        return jsonify({
            'success': True,
            'workspace': str(WORKSPACE_DIR),
            'tree': tree
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/workspace/set', methods=['POST'])
def set_workspace():
    """Change the workspace directory."""
    global WORKSPACE_DIR
    try:
        data = request.json
        new_path = Path(data.get('path'))
        
        if not new_path.exists() or not new_path.is_dir():
            return jsonify({
                'success': False,
                'error': 'Invalid directory path'
            }), 400
        
        WORKSPACE_DIR = new_path
        return jsonify({
            'success': True,
            'workspace': str(WORKSPACE_DIR)
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/file/read', methods=['POST'])
def read_file():
    """Read file contents."""
    try:
        data = request.json
        file_path = WORKSPACE_DIR / data.get('path')
        
        if not file_path.exists() or not file_path.is_file():
            return jsonify({
                'success': False,
                'error': 'File not found'
            }), 404
        
        # Check file size (limit to 10MB)
        if file_path.stat().st_size > 10 * 1024 * 1024:
            return jsonify({
                'success': False,
                'error': 'File too large (max 10MB)'
            }), 400
        
        # Try to read as text
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Detect language from extension
            extension = file_path.suffix.lower()
            language_map = {
                '.py': 'python',
                '.js': 'javascript',
                '.ts': 'typescript',
                '.jsx': 'javascript',
                '.tsx': 'typescript',
                '.html': 'html',
                '.css': 'css',
                '.json': 'json',
                '.md': 'markdown',
                '.yaml': 'yaml',
                '.yml': 'yaml',
                '.sh': 'bash',
                '.go': 'go',
                '.rs': 'rust',
                '.java': 'java',
                '.cpp': 'cpp',
                '.c': 'c',
            }
            
            return jsonify({
                'success': True,
                'content': content,
                'language': language_map.get(extension, 'plaintext'),
                'path': str(file_path.relative_to(WORKSPACE_DIR)),
                'size': file_path.stat().st_size
            })
        except UnicodeDecodeError:
            return jsonify({
                'success': False,
                'error': 'Binary file - cannot display'
            }), 400
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/file/write', methods=['POST'])
def write_file():
    """Write file contents."""
    try:
        data = request.json
        file_path = WORKSPACE_DIR / data.get('path')
        content = data.get('content')
        
        # Create parent directories if they don't exist
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(content)
        
        return jsonify({
            'success': True,
            'path': str(file_path.relative_to(WORKSPACE_DIR))
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/file/create', methods=['POST'])
def create_file():
    """Create a new file."""
    try:
        data = request.json
        file_path = WORKSPACE_DIR / data.get('path')
        
        if file_path.exists():
            return jsonify({
                'success': False,
                'error': 'File already exists'
            }), 400
        
        # Create parent directories
        file_path.parent.mkdir(parents=True, exist_ok=True)
        
        # Create empty file
        file_path.touch()
        
        return jsonify({
            'success': True,
            'path': str(file_path.relative_to(WORKSPACE_DIR))
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/api/stt/test', methods=['GET'])
def test_stt():
    """Test endpoint to check which STT is configured."""
    try:
        from tools.stt_tool import create_stt_tool
        stt_tool = create_stt_tool()
        
        # Test with dummy text
        result = stt_tool.call("test text")
        
        return jsonify({
            'success': True,
            'stt_name': stt_tool.name,
            'stt_description': stt_tool.description,
            'test_result': result.success,
            'metadata': result.metadata
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


@app.route('/observability')
def observability_dashboard():
    """Serve the observability dashboard page."""
    return render_template('observability.html')


@app.route('/api/observability/data')
def get_observability_data():
    """Get observability data (records and summary stats)."""
    try:
        tracker = get_tracker()
        
        return jsonify({
            'success': True,
            'records': tracker.get_all_records(),
            'summary': tracker.get_summary_stats()
        })
    except Exception as e:
        return jsonify({
            'success': False,
            'error': str(e)
        }), 500


# WebSocket event handlers for voice interaction
@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    emit('status', {'message': 'Connected to Voice First IDE', 'type': 'success'})


@socketio.on('voice_command')
def handle_voice_command(data):
    """Process voice command through the agent pipeline."""
    tracker = get_tracker()
    
    try:
        # Get the audio data or text input
        audio_data = data.get('audio')  # base64 encoded audio
        text_input = data.get('text')  # or direct text input
        context = data.get('context', {})
        
        # Initialize logging
        reset_logger()
        logger = get_logger()
        logger.log_pipeline_start(text_input if text_input else "Voice input")
        
        # Start observability tracking
        query = text_input if text_input else "Voice input"
        tracker.start_tracking(query)
        
        # Emit status update
        emit('agent_status', {
            'stage': 'speech',
            'agent': 'Speech Agent',
            'status': 'processing',
            'message': 'Transcribing voice input...'
        })
        
        # Stage 1: Speech to Text
        tracker.track_agent_start('Speech Agent', 'speech')
        speech_agent = SpeechAgent()
        stt_tool = create_stt_tool()
        speech_agent.add_tool(stt_tool)
        
        # Use text input directly if provided (for testing), otherwise process audio
        if text_input:
            transcript = text_input
            speech_result = type('obj', (object,), {
                'success': True,
                'data': transcript,
                'metadata': {'source': 'web_speech_api'}
            })()
        else:
            speech_result = speech_agent.execute(audio_data, context)
            if not speech_result.success:
                tracker.track_agent_end('Speech Agent', 'speech', [stt_tool.name], 0, False)
                tracker.end_tracking(success=False, error=speech_result.error)
                emit('agent_error', {
                    'stage': 'speech',
                    'error': speech_result.error
                })
                return
            transcript = speech_result.data
        
        # Track speech agent completion
        tracker.track_tool_usage(stt_tool.name, audio_data or text_input, transcript, 0, 0)
        tracker.track_agent_end('Speech Agent', 'speech', [stt_tool.name], 0, True)
        
        # Send transcript to client with STT source info
        stt_source = speech_result.metadata.get('source', 'unknown')
        stt_model = speech_result.metadata.get('model', '')
        
        emit('transcript', {
            'text': transcript,
            'source': stt_source,
            'model': stt_model
        })
        
        # Show which STT was used
        stt_display = ''
        if stt_source == 'web_speech_api':
            stt_display = '🌐 Web Speech API (Browser)'
        elif stt_source == 'google_stt_enhanced' or stt_model == 'google_stt_enhanced':
            stt_display = '☁️ Google Cloud STT (SOTA Enhanced)'
        else:
            stt_display = '🎤 Speech processed'
        
        emit('agent_status', {
            'stage': 'speech',
            'agent': 'Speech Agent',
            'status': 'completed',
            'message': f'Transcribed: "{transcript}"<br><small>{stt_display}</small>'
        })
        
        # Stage 2: Security validation
        tracker.track_agent_start('Security Agent', 'security')
        emit('agent_status', {
            'stage': 'security',
            'agent': 'Security Agent',
            'status': 'processing',
            'message': 'Validating command safety...'
        })
        
        security_agent = SecurityAgent()
        sanitizer_tool = SanitizerTool()
        security_agent.add_tool(sanitizer_tool)
        security_result = security_agent.execute(transcript, context)
        
        if not security_result.success:
            tracker.track_agent_end('Security Agent', 'security', [sanitizer_tool.name], 0, False)
            tracker.end_tracking(success=False, error=security_result.error)
            emit('agent_error', {
                'stage': 'security',
                'error': security_result.error
            })
            return
        
        sanitized_command = security_result.data
        tracker.track_tool_usage(sanitizer_tool.name, transcript, sanitized_command, 0, 0)
        tracker.track_agent_end('Security Agent', 'security', [sanitizer_tool.name], 0, True)
        emit('agent_status', {
            'stage': 'security',
            'agent': 'Security Agent',
            'status': 'completed',
            'message': 'Command validated and sanitized'
        })
        
        # Stage 3: Planning
        tracker.track_agent_start('Reasoning Agent', 'reasoning')
        emit('agent_status', {
            'stage': 'reasoning',
            'agent': 'Reasoning Agent',
            'status': 'processing',
            'message': 'Creating execution plan...'
        })
        
        reasoning_agent = ReasoningAgent()
        llm_tool_reasoning = GeminiLLMTool()
        reasoning_agent.add_tool(llm_tool_reasoning)
        reasoning_result = reasoning_agent.execute(sanitized_command, context)
        
        if not reasoning_result.success:
            tracker.track_agent_end('Reasoning Agent', 'reasoning', [llm_tool_reasoning.name], 0, False)
            tracker.end_tracking(success=False, error=reasoning_result.error)
            emit('agent_error', {
                'stage': 'reasoning',
                'error': reasoning_result.error
            })
            return
        
        plan = reasoning_result.data
        # Track reasoning tokens (estimate from plan size)
        reasoning_tokens = len(str(plan)) // 4
        tracker.track_tool_usage(llm_tool_reasoning.name, sanitized_command, plan, reasoning_tokens, 0)
        tracker.track_agent_end('Reasoning Agent', 'reasoning', [llm_tool_reasoning.name], reasoning_tokens, True)
        emit('agent_status', {
            'stage': 'reasoning',
            'agent': 'Reasoning Agent',
            'status': 'completed',
            'message': f'Plan created with {plan["step_count"]} steps',
            'data': plan
        })
        
        # Stage 4: Code Generation
        tracker.track_agent_start('Coder Agent', 'coding')
        emit('agent_status', {
            'stage': 'coding',
            'agent': 'Coder Agent',
            'status': 'processing',
            'message': 'Generating code...'
        })
        
        coder_agent = CoderAgent()
        llm_tool_coder = GeminiLLMTool()
        coder_agent.add_tool(llm_tool_coder)
        
        # Add file context if available
        if context.get('current_file'):
            coder_context = {
                'language': context.get('language', 'python'),
                'existing_code': context.get('file_content', ''),
                'file_path': context.get('current_file')
            }
        else:
            coder_context = {'language': context.get('language', 'python')}
        
        coder_result = coder_agent.execute(plan, coder_context)
        
        if not coder_result.success:
            tracker.track_agent_end('Coder Agent', 'coding', [llm_tool_coder.name], 0, False)
            tracker.end_tracking(success=False, error=coder_result.error)
            emit('agent_error', {
                'stage': 'coding',
                'error': coder_result.error
            })
            return
        
        code_data = coder_result.data
        # Track coder tokens (estimate from code size)
        coder_tokens = len(code_data['code']) // 4
        tracker.track_tool_usage(llm_tool_coder.name, plan, code_data['code'], coder_tokens, 0)
        tracker.track_agent_end('Coder Agent', 'coding', [llm_tool_coder.name], coder_tokens, True)
        emit('agent_status', {
            'stage': 'coding',
            'agent': 'Coder Agent',
            'status': 'completed',
            'message': f'Code generated ({len(code_data["code"])} characters)'
        })
        
        # Send the generated code back
        emit('code_generated', {
            'code': code_data['code'],
            'language': code_data.get('language', 'python'),
            'command': code_data.get('command', ''),
            'plan': plan
        })
        
        # Log completion
        logger.log_pipeline_end(success=True)
        
        # End observability tracking
        tracker.end_tracking(success=True)
        
        emit('pipeline_complete', {
            'success': True,
            'log_file': logger.get_log_file_path(),
            'json_log': logger.get_json_log_path()
        })
        
    except Exception as e:
        # End tracking with error
        tracker.end_tracking(success=False, error=str(e))
        
        emit('agent_error', {
            'stage': 'unknown',
            'error': str(e)
        })
        import traceback
        traceback.print_exc()


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    print('Client disconnected')


if __name__ == '__main__':
    import os
    port = int(os.environ.get('PORT', 8081))
    print("🎙️ Voice First IDE Starting...")
    print(f"📁 Workspace: {WORKSPACE_DIR}")
    print(f"🌐 Open http://localhost:{port} in your browser")
    socketio.run(app, debug=False, host='0.0.0.0', port=port)
