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
from agents.analyzer_agent import AnalyzerAgent

# Import tools
from tools.stt_tool import create_stt_tool
from tools.sanitizer_tool import SanitizerTool
from tools.llm_tool import GeminiLLMTool

# Import logging
from utils.logger import get_logger, reset_logger

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


# WebSocket event handlers for voice interaction
@socketio.on('connect')
def handle_connect():
    """Handle client connection."""
    emit('status', {'message': 'Connected to Voice First IDE', 'type': 'success'})


@socketio.on('voice_command')
def handle_voice_command(data):
    """Process voice command through the agent pipeline."""
    try:
        # Get the audio data or text input
        audio_data = data.get('audio')  # base64 encoded audio
        text_input = data.get('text')  # or direct text input
        context = data.get('context', {})
        
        # Initialize logging
        reset_logger()
        logger = get_logger()
        logger.log_pipeline_start(text_input if text_input else "Voice input")
        
        # Emit status update
        emit('agent_status', {
            'stage': 'speech',
            'agent': 'Speech Agent',
            'status': 'processing',
            'message': 'Transcribing voice input...'
        })
        
        # Stage 1: Speech to Text
        speech_agent = SpeechAgent()
        speech_agent.add_tool(create_stt_tool())
        
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
                emit('agent_error', {
                    'stage': 'speech',
                    'error': speech_result.error
                })
                return
            transcript = speech_result.data
        
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
        emit('agent_status', {
            'stage': 'security',
            'agent': 'Security Agent',
            'status': 'processing',
            'message': 'Validating command safety...'
        })
        
        security_agent = SecurityAgent()
        security_agent.add_tool(SanitizerTool())
        security_result = security_agent.execute(transcript, context)
        
        if not security_result.success:
            emit('agent_error', {
                'stage': 'security',
                'error': security_result.error
            })
            return
        
        sanitized_command = security_result.data
        emit('agent_status', {
            'stage': 'security',
            'agent': 'Security Agent',
            'status': 'completed',
            'message': 'Command validated and sanitized'
        })
        
        # Stage 3: Planning
        emit('agent_status', {
            'stage': 'reasoning',
            'agent': 'Reasoning Agent',
            'status': 'processing',
            'message': 'Creating execution plan...'
        })
        
        reasoning_agent = ReasoningAgent()
        reasoning_agent.add_tool(GeminiLLMTool())
        reasoning_result = reasoning_agent.execute(sanitized_command, context)
        
        if not reasoning_result.success:
            emit('agent_error', {
                'stage': 'reasoning',
                'error': reasoning_result.error
            })
            return
        
        plan = reasoning_result.data
        emit('agent_status', {
            'stage': 'reasoning',
            'agent': 'Reasoning Agent',
            'status': 'completed',
            'message': f'Plan created with {plan["step_count"]} steps',
            'data': plan
        })
        
        # Stage 4: Code Generation
        emit('agent_status', {
            'stage': 'coding',
            'agent': 'Coder Agent',
            'status': 'processing',
            'message': 'Generating code...'
        })
        
        coder_agent = CoderAgent()
        coder_agent.add_tool(GeminiLLMTool())
        
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
            emit('agent_error', {
                'stage': 'coding',
                'error': coder_result.error
            })
            return
        
        code_data = coder_result.data
        emit('agent_status', {
            'stage': 'coding',
            'agent': 'Coder Agent',
            'status': 'completed',
            'message': f'Code generated ({len(code_data["code"])} characters)'
        })
        
        # Send the generated code back (with suggested filename)
        emit('code_generated', {
            'code': code_data['code'],
            'language': code_data.get('language', 'python'),
            'command': code_data.get('command', ''),
            'suggested_filename': code_data.get('suggested_filename', None),
            'plan': plan
        })
        
        # Log completion
        logger.log_pipeline_end(success=True)
        
        emit('pipeline_complete', {
            'success': True,
            'log_file': logger.get_log_file_path(),
            'json_log': logger.get_json_log_path()
        })
        
    except Exception as e:
        emit('agent_error', {
            'stage': 'unknown',
            'error': str(e)
        })
        import traceback
        traceback.print_exc()


@socketio.on('question')
def handle_question(data):
    """Handle explanation/question requests without generating files."""
    try:
        text = data.get('text', '')
        current_file = data.get('currentFile')
        
        emit('status', {'message': 'Thinking...', 'type': 'info'})
        
        # Use LLM to answer the question
        llm_tool = GeminiLLMTool()
        
        prompt = f"""You are a helpful coding assistant. Answer this question clearly and concisely:

Question: {text}

{f"Context: User is looking at file: {current_file}" if current_file else ""}

Provide a clear, helpful answer. If the question is about code, explain it well. Do NOT generate code files unless explicitly asked to create/write/build something."""
        
        result = llm_tool.call(prompt)
        
        if result.success:
            # Send response back as a message
            emit('status', {
                'message': result.output,
                'type': 'answer'
            })
        else:
            emit('agent_error', {
                'stage': 'question',
                'error': result.error
            })
    except Exception as e:
        emit('agent_error', {
            'stage': 'question',
            'error': str(e)
        })
        import traceback
        traceback.print_exc()


@socketio.on('analyze_codebase')
def handle_analyze_codebase(data):
    """Analyze the current workspace and generate mental model."""
    try:
        is_external = data.get('isExternal', False)
        
        emit('status', {'message': 'Analyzing codebase...', 'type': 'info'})
        
        if is_external:
            # Handle external folder analysis using client-provided file info
            file_info = data.get('fileInfo', {})
            
            # Create a prompt with the file structure
            llm_tool = GeminiLLMTool()
            
            files = file_info.get('files', [])
            folder_name = file_info.get('folderName', 'Unknown')
            
            # Build file list
            file_list = '\n'.join([f"- {f['path']} ({f['extension']})" for f in files[:100]])
            if len(files) > 100:
                file_list += f"\n... and {len(files) - 100} more files"
            
            # Count by extension
            ext_count = {}
            for f in files:
                ext = f['extension']
                ext_count[ext] = ext_count.get(ext, 0) + 1
            
            lang_dist = ', '.join([f"{ext} ({count})" for ext, count in sorted(ext_count.items(), key=lambda x: -x[1])])
            
            prompt = f"""You are an expert software architect. Analyze this codebase and provide a comprehensive mental model.

Project: {folder_name}
Total Files: {len(files)}
Languages: {lang_dist}

File Structure:
{file_list}

Generate a comprehensive mental model document in Markdown format that includes:

1. **Project Overview** - What this project appears to be based on file structure
2. **Architecture** - Likely architecture and design patterns
3. **Key Components** - Main modules/components based on folder structure
4. **Technology Stack** - Languages, frameworks, and tools used
5. **File Organization** - How the codebase is structured
6. **Entry Points** - Main files to start understanding the code
7. **Dependencies & Integration** - How components likely interact
8. **Development Workflow** - Likely dev/build/test processes

Make it clear, concise, and actionable."""
            
            result = llm_tool.call(prompt)
            
            if result.success:
                emit('codebase_analysis', {
                    'analysis': result.output,
                    'file_count': len(files),
                    'language_distribution': ext_count
                })
            else:
                emit('agent_error', {
                    'stage': 'analyzer',
                    'error': result.error
                })
        else:
            # Handle regular workspace folder analysis
            analyzer_agent = AnalyzerAgent()
            analyzer_agent.add_tool(GeminiLLMTool())
            
            # Execute analysis
            analysis_input = {
                'action': 'analyze',
                'path': str(WORKSPACE_DIR)
            }
            context = {'workspace_path': str(WORKSPACE_DIR)}
            
            result = analyzer_agent.execute(analysis_input, context)
            
            if result.success:
                emit('codebase_analysis', {
                    'analysis': result.data['analysis'],
                    'file_count': result.data['file_count'],
                    'language_distribution': result.data['language_distribution']
                })
            else:
                emit('agent_error', {
                    'stage': 'analyzer',
                    'error': result.error
                })
    except Exception as e:
        emit('agent_error', {
            'stage': 'analyzer',
            'error': str(e)
        })
        import traceback
        traceback.print_exc()


@socketio.on('disconnect')
def handle_disconnect():
    """Handle client disconnection."""
    print('Client disconnected')


if __name__ == '__main__':
    print("🎙️ Voice First IDE Starting...")
    print(f"📁 Workspace: {WORKSPACE_DIR}")
    print(f"🌐 Open http://localhost:8081 in your browser")
    socketio.run(app, debug=True, host='0.0.0.0', port=8081)
