// Voice First IDE - Main Application
class VoiceFirstIDE {
    constructor() {
        this.socket = null;
        this.editor = null;
        this.currentFile = null;
        this.fileTree = null;
        this.isRecording = false;
        this.mediaRecorder = null;
        this.audioChunks = [];
        this.activeWorkspacePath = null;  // Track user's opened folder
        this.isExternalWorkspace = false;  // Track if using external folder
        
        this.init();
    }
    
    async init() {
        // Initialize Socket.IO connection
        this.initSocket();
        
        // Initialize Monaco Editor
        await this.initEditor();
        
        // Load file tree
        await this.loadFileTree();
        
        // Setup event listeners
        this.setupEventListeners();
        
        // Setup resize handles
        this.setupResizeHandles();
    }
    
    initSocket() {
        this.socket = io();
        
        this.socket.on('connect', () => {
            this.updateConnectionStatus(true);
            this.addMessage('assistant', 'Connected to Voice First IDE server!');
        });
        
        this.socket.on('disconnect', () => {
            this.updateConnectionStatus(false);
        });
        
        this.socket.on('status', (data) => {
            this.addMessage('assistant', data.message);
        });
        
        this.socket.on('transcript', (data) => {
            this.addMessage('user', data.text);
        });
        
        this.socket.on('agent_status', (data) => {
            this.updateAgentStatus(data.stage, data.status, data.message);
            
            if (data.status === 'completed' && data.data) {
                // Show plan steps if available
                if (data.stage === 'reasoning' && data.data.steps) {
                    const stepsHtml = data.data.steps.map((step, i) => 
                        `${i + 1}. ${step}`
                    ).join('<br>');
                    this.addMessage('assistant', `<strong>Execution Plan:</strong><br>${stepsHtml}`);
                }
            }
        });
        
        this.socket.on('agent_error', (data) => {
            this.updateAgentStatus(data.stage, 'error', data.error);
            this.addMessage('assistant', `❌ Error in ${data.stage}: ${data.error}`);
            this.resetAgentStatus();
        });
        
        this.socket.on('code_generated', (data) => {
            this.addMessage('assistant', `✅ Code generated successfully! (${data.code.length} characters)`);
            
            // Store generated code and metadata
            this.lastGeneratedCode = data.code;
            this.lastGeneratedLanguage = data.language;
            this.lastSuggestedFilename = data.suggested_filename;
            
            // Check if we're editing an existing file or creating new
            // If editor has content and a file is open, it's an edit
            const hasExistingContent = this.currentFile && 
                                      this.editor.getValue().trim().length > 0 &&
                                      document.getElementById('editorContainer').style.display !== 'none';
            
            if (hasExistingContent) {
                // Editing existing file - show diff view
                this.showDiffApproval(data.code);
            } else {
                // Creating new file - show in editor immediately
                this.createAndShowNewFile(data.code, data.language, data.suggested_filename);
            }
        });
        
        this.socket.on('pipeline_complete', (data) => {
            this.addMessage('assistant', '🎉 Pipeline complete! Code is ready.');
            setTimeout(() => this.resetAgentStatus(), 3000);
        });
        
        this.socket.on('codebase_analysis', (data) => {
            this.addMessage('assistant', '🧠 Codebase analysis complete!');
            
            // Create and save the mental model markdown file
            this.createAnalysisFile(data.analysis, data.file_count, data.language_distribution);
        });
    }
    
    async initEditor() {
        return new Promise((resolve) => {
            require.config({ 
                paths: { 
                    vs: 'https://cdnjs.cloudflare.com/ajax/libs/monaco-editor/0.45.0/min/vs' 
                } 
            });
            
            require(['vs/editor/editor.main'], () => {
                this.editor = monaco.editor.create(document.getElementById('monacoEditor'), {
                    value: '',
                    language: 'python',
                    theme: 'vs-dark',
                    automaticLayout: true,
                    fontSize: 14,
                    minimap: { enabled: true },
                    scrollBeyondLastLine: false,
                    renderWhitespace: 'selection',
                    tabSize: 4,
                });
                
                // Add save command (Ctrl+S / Cmd+S)
                this.editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, () => {
                    this.saveCurrentFile();
                });
                
                resolve();
            });
        });
    }
    
    async loadFileTree() {
        try {
            const response = await fetch('/api/workspace/files');
            const data = await response.json();
            
            if (data.success) {
                this.fileTree = data.tree;
                document.getElementById('workspacePathText').textContent = data.workspace;
                this.renderFileTree(data.tree);
            }
        } catch (error) {
            console.error('Failed to load file tree:', error);
            this.addMessage('assistant', '❌ Failed to load workspace files');
        }
    }
    
    renderFileTree(tree, container = null) {
        const fileTreeEl = container || document.getElementById('fileTree');
        
        if (!container) {
            fileTreeEl.innerHTML = '';
        }
        
        tree.forEach(item => {
            if (item.type === 'directory') {
                const folderEl = document.createElement('div');
                folderEl.className = 'folder-item';
                folderEl.innerHTML = `
                    <i class="fas fa-chevron-right"></i>
                    <i class="fas fa-folder"></i>
                    <span>${item.name}</span>
                `;
                
                const childrenEl = document.createElement('div');
                childrenEl.className = 'folder-children';
                childrenEl.style.display = 'none';
                
                folderEl.addEventListener('click', (e) => {
                    e.stopPropagation();
                    folderEl.classList.toggle('expanded');
                    childrenEl.style.display = childrenEl.style.display === 'none' ? 'block' : 'none';
                });
                
                fileTreeEl.appendChild(folderEl);
                fileTreeEl.appendChild(childrenEl);
                
                if (item.children && item.children.length > 0) {
                    this.renderFileTree(item.children, childrenEl);
                }
            } else {
                const fileEl = document.createElement('div');
                fileEl.className = 'file-item';
                fileEl.dataset.path = item.path;
                
                const icon = this.getFileIcon(item.name);
                fileEl.innerHTML = `
                    <i class="${icon}"></i>
                    <span>${item.name}</span>
                `;
                
                fileEl.addEventListener('click', () => {
                    this.openFile(item.path);
                });
                
                fileTreeEl.appendChild(fileEl);
            }
        });
    }
    
    getFileIcon(filename) {
        const ext = filename.split('.').pop().toLowerCase();
        const iconMap = {
            'py': 'fab fa-python',
            'js': 'fab fa-js',
            'ts': 'fab fa-js',
            'html': 'fab fa-html5',
            'css': 'fab fa-css3',
            'json': 'fas fa-file-code',
            'md': 'fab fa-markdown',
            'txt': 'fas fa-file-alt',
            'sh': 'fas fa-terminal',
            'go': 'fab fa-golang',
            'rs': 'fas fa-file-code',
            'java': 'fab fa-java',
        };
        return iconMap[ext] || 'fas fa-file';
    }
    
    async openFile(path) {
        try {
            // Check if this is an external file
            if (this.externalFiles && this.externalFiles.has(path)) {
                const file = this.externalFiles.get(path);
                const content = await file.text();
                
                // Detect language
                const ext = file.name.split('.').pop().toLowerCase();
                const languageMap = {
                    'py': 'python',
                    'js': 'javascript',
                    'ts': 'typescript',
                    'html': 'html',
                    'css': 'css',
                    'json': 'json',
                    'md': 'markdown',
                };
                const language = languageMap[ext] || 'plaintext';
                
                this.currentFile = {
                    path: path,
                    language: language,
                    content: content,
                    isExternal: true
                };
                
                // Update editor
                this.editor.setValue(content);
                monaco.editor.setModelLanguage(this.editor.getModel(), language);
                
                // Show editor
                document.getElementById('welcomeScreen').style.display = 'none';
                document.getElementById('editorContainer').style.display = 'block';
                
                // Update active file in tree
                document.querySelectorAll('.file-item').forEach(el => el.classList.remove('active'));
                const fileEl = document.querySelector(`.file-item[data-path="${path}"]`);
                if (fileEl) fileEl.classList.add('active');
                
                // Update tab
                this.updateTab(path);
                
                this.addMessage('assistant', `Opened: ${path}`);
                return;
            }
            
            // Otherwise, load from backend
            const response = await fetch('/api/file/read', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ path })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.currentFile = {
                    path: data.path,
                    language: data.language,
                    content: data.content
                };
                
                // Update editor
                this.editor.setValue(data.content);
                monaco.editor.setModelLanguage(this.editor.getModel(), data.language);
                
                // Show editor, hide welcome screen
                document.getElementById('welcomeScreen').style.display = 'none';
                document.getElementById('editorContainer').style.display = 'block';
                
                // Update active file in tree
                document.querySelectorAll('.file-item').forEach(el => el.classList.remove('active'));
                const fileEl = document.querySelector(`.file-item[data-path="${path}"]`);
                if (fileEl) fileEl.classList.add('active');
                
                // Update tab
                this.updateTab(path);
                
                this.addMessage('assistant', `Opened: ${path}`);
            } else {
                this.addMessage('assistant', `❌ Failed to open file: ${data.error}`);
            }
        } catch (error) {
            console.error('Failed to open file:', error);
            this.addMessage('assistant', '❌ Failed to open file');
        }
    }
    
    updateTab(path) {
        const tabsEl = document.getElementById('editorTabs');
        tabsEl.innerHTML = `
            <div class="tab active">
                <i class="${this.getFileIcon(path)}"></i>
                <span>${path.split('/').pop()}</span>
            </div>
        `;
    }
    
    async saveCurrentFile() {
        if (!this.currentFile) {
            this.addMessage('assistant', 'No file open to save');
            return;
        }
        
        try {
            const content = this.editor.getValue();
            
            const response = await fetch('/api/file/write', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({
                    path: this.currentFile.path,
                    content: content
                })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.addMessage('assistant', `✅ Saved: ${this.currentFile.path}`);
            } else {
                this.addMessage('assistant', `❌ Failed to save: ${data.error}`);
            }
        } catch (error) {
            console.error('Failed to save file:', error);
            this.addMessage('assistant', '❌ Failed to save file');
        }
    }
    
    setupEventListeners() {
        // Microphone button
        document.getElementById('micButton').addEventListener('click', () => {
            if (this.isRecording) {
                this.stopRecording();
                this.addMessage('assistant', 'Recording stopped.');
            } else {
                this.startRecording();
            }
        });
        
        // Send text button
        document.getElementById('sendText').addEventListener('click', () => {
            this.sendTextCommand();
        });
        
        // Text input Enter key
        document.getElementById('textInput').addEventListener('keypress', (e) => {
            if (e.key === 'Enter') {
                this.sendTextCommand();
            }
        });
        
        // Open folder
        document.getElementById('openFolder').addEventListener('click', () => {
            document.getElementById('folderPickerInput').click();
        });
        
        // Open single file
        document.getElementById('openFile').addEventListener('click', () => {
            document.getElementById('filePickerInput').click();
        });
        
        // Handle folder selection
        document.getElementById('folderPickerInput').addEventListener('change', (e) => {
            this.handleFolderSelection(e.target.files);
        });
        
        // Handle file selection
        document.getElementById('filePickerInput').addEventListener('change', (e) => {
            this.handleFileSelection(e.target.files[0]);
        });
        
        // Refresh files
        document.getElementById('refreshFiles').addEventListener('click', () => {
            this.loadFileTree();
        });
        
        // New file
        document.getElementById('newFile').addEventListener('click', () => {
            const filename = prompt('Enter filename:');
            if (filename) {
                this.createNewFile(filename);
            }
        });
        
        // Clear chat
        document.getElementById('clearChat').addEventListener('click', () => {
            const conversationEl = document.getElementById('conversation');
            conversationEl.innerHTML = `
                <div class="message assistant">
                    <div class="message-icon"><i class="fas fa-robot"></i></div>
                    <div class="message-content">
                        <p>Chat cleared. How can I help you?</p>
                    </div>
                </div>
            `;
        });
        
        // Analyze codebase
        document.getElementById('analyzeCodebase').addEventListener('click', () => {
            this.analyzeCodebase();
        });
    }
    
    async startRecording() {
        try {
            // CURRENT IMPLEMENTATION: Using Browser's Web Speech API
            // This transcribes audio in the browser and sends only TEXT to the backend
            // 
            // TO USE GOOGLE CLOUD STT: See GOOGLE_STT_SETUP.md for instructions
            // You would need to capture raw audio with MediaRecorder and send audio bytes to backend
            // 
            // For now, this provides instant transcription without backend setup
            
            if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
                this.addMessage('assistant', 
                    '❌ Speech recognition not supported in this browser. ' +
                    'Please use Chrome, Edge, or Safari, or type your command instead.'
                );
                return;
            }
            
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.recognition = new SpeechRecognition();
            
            // FIXED: Make it continuous - no auto-stop!
            this.recognition.continuous = true;  // Keep listening until user clicks stop
            this.recognition.interimResults = true;  // Show results in real-time
            this.recognition.lang = 'en-US';
            this.recognition.maxAlternatives = 1;
            
            // Store partial transcript
            this.currentTranscript = '';
            
            this.recognition.onstart = () => {
                this.isRecording = true;
                document.getElementById('micButton').classList.add('recording');
                
                // SHOW STT CLEARLY AT START
                this.addMessage('assistant', 
                    `<div style="padding: 15px; background: linear-gradient(135deg, var(--accent-blue), var(--accent-purple)); border-radius: 8px; border: 2px solid var(--accent-green);">
                        <p style="font-size: 16px; font-weight: bold; color: white; margin-bottom: 8px;">🎤 Recording Started</p>
                        <p style="font-size: 14px; color: white; margin-bottom: 8px;"><strong>STT Engine:</strong> Google Web Speech API (Browser-based)</p>
                        <p style="font-size: 12px; color: white; opacity: 0.9;">• Speak naturally, take your time<br>• Click microphone again when done<br>• No rush - I'm listening continuously!</p>
                    </div>`
                );
            };
            
            this.recognition.onresult = (event) => {
                // Build full transcript from all results
                let finalTranscript = '';
                let interimTranscript = '';
                
                for (let i = event.resultIndex; i < event.results.length; i++) {
                    const transcript = event.results[i][0].transcript;
                    if (event.results[i].isFinal) {
                        finalTranscript += transcript + ' ';
                    } else {
                        interimTranscript += transcript;
                    }
                }
                
                // Update current transcript
                if (finalTranscript) {
                    this.currentTranscript += finalTranscript;
                }
                
                // Show real-time transcript (optional - can be removed if too noisy)
                if (interimTranscript && !finalTranscript) {
                    // Show interim results in a temporary message (updates live)
                    const lastMsg = document.querySelector('.conversation .message:last-child');
                    if (lastMsg && lastMsg.classList.contains('interim')) {
                        lastMsg.querySelector('.message-content p').textContent = '🎤 ' + interimTranscript + '...';
                    } else {
                        const msg = document.createElement('div');
                        msg.className = 'message assistant interim';
                        msg.innerHTML = `
                            <div class="message-icon"><i class="fas fa-microphone-lines"></i></div>
                            <div class="message-content"><p>🎤 ${interimTranscript}...</p></div>
                        `;
                        document.getElementById('conversation').appendChild(msg);
                    }
                }
            };
            
            this.recognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
                
                // Don't stop on "no-speech" error - user might be thinking
                if (event.error === 'no-speech') {
                    this.addMessage('assistant', '🔇 Still listening... take your time!');
                    return;  // Keep recording!
                }
                
                this.isRecording = false;
                document.getElementById('micButton').classList.remove('recording');
                
                let errorMsg = 'Speech recognition error: ';
                switch(event.error) {
                    case 'audio-capture':
                        errorMsg += 'No microphone found. Please check your audio settings.';
                        break;
                    case 'not-allowed':
                        errorMsg += 'Microphone permission denied. Please allow microphone access.';
                        break;
                    case 'aborted':
                        errorMsg += 'Recording was aborted.';
                        break;
                    default:
                        errorMsg += event.error;
                }
                this.addMessage('assistant', `❌ ${errorMsg}`);
            };
            
            this.recognition.onend = () => {
                // Only process if we have a transcript and user didn't manually stop
                if (this.currentTranscript.trim() && this.isRecording) {
                    this.processFinalTranscript();
                }
                
                this.isRecording = false;
                document.getElementById('micButton').classList.remove('recording');
            };
            
            // Start recognition
            this.recognition.start();
            
        } catch (error) {
            console.error('Speech recognition error:', error);
            this.addMessage('assistant', 
                '❌ Failed to start speech recognition. Please check browser permissions.'
            );
        }
    }
    
    stopRecording() {
        if (this.recognition && this.isRecording) {
            this.isRecording = false;  // Set flag before stopping
            this.recognition.stop();
            document.getElementById('micButton').classList.remove('recording');
            
            // Remove interim message if exists
            const interimMsg = document.querySelector('.message.interim');
            if (interimMsg) {
                interimMsg.remove();
            }
            
            // Process the final transcript
            if (this.currentTranscript && this.currentTranscript.trim()) {
                this.processFinalTranscript();
            } else {
                this.addMessage('assistant', '❌ No speech detected. Please try again.');
            }
        }
    }
    
    processFinalTranscript() {
        const transcript = this.currentTranscript.trim();
        
        if (!transcript) return;
        
        // Show what was captured
        this.addMessage('user', transcript);
        this.addMessage('assistant', 
            `<div style="padding: 10px; background: var(--bg-tertiary); border-radius: 6px; border-left: 3px solid var(--accent-green);">
                <p style="margin-bottom: 5px; font-weight: bold; color: var(--accent-green);">✅ Transcription Complete</p>
                <p style="margin-bottom: 5px; font-size: 13px;">Captured: <strong>${transcript.length}</strong> characters</p>
                <p style="font-size: 12px; color: var(--text-secondary);">Using: <strong>Google Web Speech API</strong> (Browser)</p>
            </div>`
        );
        
        // Send to backend for processing
        this.processVoiceCommand(transcript);
        
        // Reset transcript
        this.currentTranscript = '';
    }
    
    processVoiceCommand(transcript) {
        // Check if this is a codebase analysis request
        const lowerText = transcript.toLowerCase();
        const isAnalysisRequest = 
            lowerText.includes('analyze codebase') ||
            lowerText.includes('analyse codebase') ||
            lowerText.includes('explain codebase') ||
            lowerText.includes('explain the codebase') ||
            lowerText.includes('mental model') ||
            lowerText.includes('understand the code') ||
            lowerText.includes('understand codebase') ||
            lowerText.includes('overview of the code') ||
            lowerText.includes('show me the codebase');
        
        if (isAnalysisRequest) {
            this.analyzeCodebase();
            return;
        }
        
        // Check if this is a code generation request or just a question
        const isCodeRequest = this.isCodeGenerationRequest(transcript);
        
        if (!isCodeRequest) {
            // For non-code requests (explanations, questions), just respond
            this.socket.emit('question', {
                text: transcript,
                currentFile: this.currentFile ? this.currentFile.path : null
            });
            return;
        }
        
        // Get current file context if available
        const context = {};
        if (this.currentFile) {
            context.current_file = this.currentFile.path;
            context.language = this.currentFile.language;
            context.file_content = this.editor.getValue();
        }
        
        // Add workspace info for external folders
        context.is_external_workspace = this.isExternalWorkspace;
        context.active_workspace = this.activeWorkspacePath;
        
        // Send to backend via WebSocket
        this.socket.emit('voice_command', {
            text: transcript,
            context: context
        });
    }
    
    sendTextCommand() {
        const input = document.getElementById('textInput');
        const text = input.value.trim();
        
        if (!text) return;
        
        // Clear input
        input.value = '';
        
        // Show user message first
        this.addMessage('user', text);
        
        // Check if this is a codebase analysis request
        const lowerText = text.toLowerCase();
        const isAnalysisRequest = 
            lowerText.includes('analyze codebase') ||
            lowerText.includes('analyse codebase') ||
            lowerText.includes('explain codebase') ||
            lowerText.includes('explain the codebase') ||
            lowerText.includes('mental model') ||
            lowerText.includes('understand the code') ||
            lowerText.includes('understand codebase') ||
            lowerText.includes('overview of the code') ||
            lowerText.includes('show me the codebase');
        
        if (isAnalysisRequest) {
            this.analyzeCodebase();
            return;
        }
        
        // Check if this is a code generation request or just a question
        const isCodeRequest = this.isCodeGenerationRequest(text);
        
        if (!isCodeRequest) {
            // For non-code requests (explanations, questions), just respond, don't generate files
            this.socket.emit('question', {
                text: text,
                currentFile: this.currentFile ? this.currentFile.path : null
            });
            return;
        }
        
        // Get current file context if available
        const context = {};
        if (this.currentFile) {
            context.current_file = this.currentFile.path;
            context.language = this.currentFile.language;
            context.file_content = this.editor.getValue();
        }
        
        // Add workspace info for external folders
        context.is_external_workspace = this.isExternalWorkspace;
        context.active_workspace = this.activeWorkspacePath;
        
        // Send to backend via WebSocket
        this.socket.emit('voice_command', {
            text: text,
            context: context
        });
        
        // Show user message
        this.addMessage('user', text);
    }
    
    updateAgentStatus(stage, status, message) {
        const statusItem = document.querySelector(`.status-item[data-stage="${stage}"]`);
        if (statusItem) {
            const badge = statusItem.querySelector('.status-badge');
            badge.textContent = status;
            badge.className = `status-badge ${status}`;
        }
        
        // Add message to conversation
        const emoji = {
            'speech': '🎤',
            'security': '🛡️',
            'reasoning': '🧠',
            'coding': '👨‍💻'
        };
        
        if (status === 'processing') {
            this.addMessage('assistant', `${emoji[stage] || ''} ${message}`);
        }
    }
    
    resetAgentStatus() {
        document.querySelectorAll('.status-badge').forEach(badge => {
            badge.textContent = 'idle';
            badge.className = 'status-badge idle';
        });
    }
    
    addMessage(type, content) {
        const conversationEl = document.getElementById('conversation');
        
        const messageEl = document.createElement('div');
        messageEl.className = `message ${type}`;
        
        const icon = type === 'user' ? '<i class="fas fa-user"></i>' : '<i class="fas fa-robot"></i>';
        
        messageEl.innerHTML = `
            <div class="message-icon">${icon}</div>
            <div class="message-content"><p>${content}</p></div>
        `;
        
        conversationEl.appendChild(messageEl);
        conversationEl.scrollTop = conversationEl.scrollHeight;
    }
    
    updateConnectionStatus(connected) {
        const statusDot = document.getElementById('statusDot');
        const statusText = document.getElementById('statusText');
        
        if (connected) {
            statusDot.classList.add('connected');
            statusText.textContent = 'Connected';
        } else {
            statusDot.classList.remove('connected');
            statusText.textContent = 'Disconnected';
        }
    }
    
    async createNewFile(filename) {
        try {
            const response = await fetch('/api/file/create', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ path: filename })
            });
            
            const data = await response.json();
            
            if (data.success) {
                this.addMessage('assistant', `✅ Created: ${filename}`);
                await this.loadFileTree();
                await this.openFile(filename);
            } else {
                this.addMessage('assistant', `❌ Failed to create file: ${data.error}`);
            }
        } catch (error) {
            console.error('Failed to create file:', error);
            this.addMessage('assistant', '❌ Failed to create file');
        }
    }
    
    setupResizeHandles() {
        // Left resize handle
        const resizeLeft = document.getElementById('resizeLeft');
        const leftPanel = document.getElementById('leftPanel');
        
        this.setupResize(resizeLeft, leftPanel, 'width');
        
        // Right resize handle
        const resizeRight = document.getElementById('resizeRight');
        const rightPanel = document.getElementById('rightPanel');
        
        this.setupResize(resizeRight, rightPanel, 'width', true);
    }
    
    setupResize(handle, panel, property, reverse = false) {
        let isResizing = false;
        let startX = 0;
        let startSize = 0;
        
        handle.addEventListener('mousedown', (e) => {
            isResizing = true;
            startX = e.clientX;
            startSize = panel.offsetWidth;
            document.body.style.cursor = 'col-resize';
            e.preventDefault();
        });
        
        document.addEventListener('mousemove', (e) => {
            if (!isResizing) return;
            
            const delta = reverse ? (startX - e.clientX) : (e.clientX - startX);
            const newSize = startSize + delta;
            
            if (newSize >= parseInt(getComputedStyle(panel).minWidth)) {
                panel.style[property] = newSize + 'px';
            }
        });
        
        document.addEventListener('mouseup', () => {
            if (isResizing) {
                isResizing = false;
                document.body.style.cursor = '';
            }
        });
    }
    
    escapeHtml(text) {
        const div = document.createElement('div');
        div.textContent = text;
        return div.innerHTML;
    }
    
    async handleFolderSelection(files) {
        if (!files || files.length === 0) return;
        
        this.addMessage('assistant', `📂 Loading folder with ${files.length} files...`);
        
        // Build a virtual file tree from selected files
        const fileTree = [];
        const fileMap = new Map();
        
        for (let i = 0; i < files.length; i++) {
            const file = files[i];
            const path = file.webkitRelativePath || file.name;
            
            // Store file for later access
            fileMap.set(path, file);
            
            // Build tree structure
            const parts = path.split('/');
            let current = fileTree;
            
            for (let j = 0; j < parts.length; j++) {
                const part = parts[j];
                const isLast = j === parts.length - 1;
                
                if (isLast) {
                    // It's a file
                    current.push({
                        name: part,
                        type: 'file',
                        path: path,
                        size: file.size
                    });
                } else {
                    // It's a directory
                    let dir = current.find(item => item.name === part && item.type === 'directory');
                    if (!dir) {
                        dir = {
                            name: part,
                            type: 'directory',
                            path: parts.slice(0, j + 1).join('/'),
                            children: []
                        };
                        current.push(dir);
                    }
                    current = dir.children;
                }
            }
        }
        
        // Store file map for reading files later
        this.externalFiles = fileMap;
        this.fileTree = fileTree;
        this.isExternalWorkspace = true;
        
        // Extract workspace path from first file
        if (files.length > 0) {
            const firstFile = files[0];
            const fullPath = firstFile.webkitRelativePath || firstFile.name;
            const folderName = fullPath.split('/')[0];
            this.activeWorkspacePath = folderName;  // This is relative, but we'll track it
        }
        
        // Render the tree
        this.renderFileTree(fileTree);
        
        this.addMessage('assistant', `✅ Loaded ${files.length} files from external folder: <strong>${this.activeWorkspacePath || 'Unknown'}</strong>`);
        this.addMessage('assistant', 
            `<div style="padding: 10px; background: rgba(0, 122, 204, 0.1); border-radius: 6px; border-left: 3px solid var(--accent-blue); margin-top: 10px;">
                <p style="font-size: 12px; margin-bottom: 5px;"><strong>💡 Tip:</strong> Click the 🧠 brain icon to analyze this codebase!</p>
            </div>`
        );
    }
    
    async handleFileSelection(file) {
        if (!file) return;
        
        this.addMessage('assistant', `📄 Opening file: <strong>${file.name}</strong>`);
        
        try {
            const content = await file.text();
            
            // Detect language
            const ext = file.name.split('.').pop().toLowerCase();
            const languageMap = {
                'py': 'python',
                'js': 'javascript',
                'ts': 'typescript',
                'html': 'html',
                'css': 'css',
                'json': 'json',
                'md': 'markdown',
            };
            const language = languageMap[ext] || 'plaintext';
            
            // Set current file
            this.currentFile = {
                path: file.name,
                language: language,
                content: content,
                isExternal: true
            };
            
            // Update editor
            this.editor.setValue(content);
            monaco.editor.setModelLanguage(this.editor.getModel(), language);
            
            // Show editor
            document.getElementById('welcomeScreen').style.display = 'none';
            document.getElementById('editorContainer').style.display = 'block';
            
            // Update tab
            this.updateTab(file.name);
            
            this.addMessage('assistant', `✅ File opened! You can now edit it or use voice commands.`);
            
        } catch (error) {
            console.error('Failed to read file:', error);
            this.addMessage('assistant', `❌ Failed to read file: ${error.message}`);
        }
    }
    
    async createAndShowNewFile(code, language, suggestedFilename = null) {
        // Use suggested filename if available, otherwise generate a generic one
        let filename;
        if (suggestedFilename) {
            filename = suggestedFilename;
        } else {
            const ext = {
                'python': 'py',
                'javascript': 'js',
                'typescript': 'ts',
                'html': 'html',
                'css': 'css',
                'java': 'java',
                'go': 'go'
            }[language] || 'txt';
            
            const timestamp = new Date().toISOString().replace(/[:.]/g, '-').slice(0, -5);
            filename = `generated_${timestamp}.${ext}`;
        }
        
        // For external workspaces, we can't create files on the backend
        // Instead, offer to download or copy to clipboard
        if (this.isExternalWorkspace) {
            this.showExternalFileCreationDialog(filename, code, language);
            return;
        }
        
        this.addMessage('assistant', `🆕 Creating new file: <strong>${filename}</strong>`);
        
        try {
            // Create the file on backend
            const response = await fetch('/api/file/create', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ path: filename })
            });
            
            const result = await response.json();
            
            if (result.success) {
                // Write the generated code to the file
                const writeResponse = await fetch('/api/file/write', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        path: filename,
                        content: code
                    })
                });
                
                const writeResult = await writeResponse.json();
                
                if (writeResult.success) {
                    this.addMessage('assistant', `✅ File created and code saved!`);
                    
                    // Refresh file tree
                    await this.loadFileTree();
                    
                    // Open the new file in editor
                    await this.openFile(filename);
                    
                    this.addMessage('assistant', 
                        `📄 File <strong>${filename}</strong> is now open in the editor. ` +
                        `You can review and make any changes.`
                    );
                }
            }
        } catch (error) {
            console.error('Failed to create file:', error);
            this.addMessage('assistant', `❌ Failed to create file. You can copy the code manually.`);
        }
    }
    
    showDiffApproval(newCode) {
        const oldCode = this.editor.getValue();
        const filename = this.currentFile.path;
        
        // Store pending changes
        this.pendingChanges = {
            oldCode: oldCode,
            newCode: newCode,
            filename: filename
        };
        
        // Show diff message in right panel
        this.addMessage('assistant', 
            `🔍 Proposed changes to <strong>${filename}</strong>:<br>` +
            `<span style="color: #f48771;">• ${oldCode.split('\n').length} lines will be removed</span><br>` +
            `<span style="color: #89d185;">• ${newCode.split('\n').length} lines will be added</span>`
        );
        
        // Create approval UI in conversation (RIGHT PANEL - buttons only)
        const approvalHtml = `
            <div style="margin-top: 15px; padding: 20px; background: rgba(45, 45, 48, 0.6); border-radius: 12px; border: 1px solid rgba(0, 122, 204, 0.3); backdrop-filter: blur(10px);">
                <p style="margin-bottom: 10px; font-weight: 600; color: var(--accent-blue); font-size: 14px; display: flex; align-items: center; gap: 8px;">
                    <i class="fas fa-code-compare"></i> Review Changes
                </p>
                <p style="margin-bottom: 20px; font-size: 13px; line-height: 1.6; color: var(--text-secondary);">Review the diff in the center editor and approve or reject the changes.</p>
                <div style="display: flex; flex-direction: column; gap: 10px;">
                    <button onclick="window.ideInstance.applyChanges()" style="
                        width: 100%; 
                        padding: 12px 16px; 
                        background: rgba(78, 201, 176, 0.15); 
                        border: 1.5px solid rgba(78, 201, 176, 0.4); 
                        border-radius: 8px; 
                        color: #4ec9b0; 
                        font-weight: 600; 
                        cursor: pointer; 
                        font-size: 14px;
                        transition: all 0.2s ease;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        gap: 8px;
                    " onmouseover="this.style.background='rgba(78, 201, 176, 0.25)'; this.style.borderColor='rgba(78, 201, 176, 0.6)';" onmouseout="this.style.background='rgba(78, 201, 176, 0.15)'; this.style.borderColor='rgba(78, 201, 176, 0.4)';">
                        <i class="fas fa-check"></i> Apply Changes
                    </button>
                    <button onclick="window.ideInstance.rejectChanges()" style="
                        width: 100%; 
                        padding: 12px 16px; 
                        background: rgba(244, 135, 113, 0.15); 
                        border: 1.5px solid rgba(244, 135, 113, 0.4); 
                        border-radius: 8px; 
                        color: #f48771; 
                        font-weight: 600; 
                        cursor: pointer; 
                        font-size: 14px;
                        transition: all 0.2s ease;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        gap: 8px;
                    " onmouseover="this.style.background='rgba(244, 135, 113, 0.25)'; this.style.borderColor='rgba(244, 135, 113, 0.6)';" onmouseout="this.style.background='rgba(244, 135, 113, 0.15)'; this.style.borderColor='rgba(244, 135, 113, 0.4)';">
                        <i class="fas fa-times"></i> Reject Changes
                    </button>
                    <button onclick="window.ideInstance.showSideBySide()" style="
                        width: 100%; 
                        padding: 10px 16px; 
                        background: rgba(60, 60, 60, 0.3); 
                        border: 1px solid rgba(62, 62, 66, 0.5); 
                        border-radius: 8px; 
                        color: var(--text-secondary); 
                        cursor: pointer; 
                        font-size: 13px;
                        transition: all 0.2s ease;
                        display: flex;
                        align-items: center;
                        justify-content: center;
                        gap: 8px;
                    " onmouseover="this.style.background='rgba(60, 60, 60, 0.5)'; this.style.color='var(--text-primary)';" onmouseout="this.style.background='rgba(60, 60, 60, 0.3)'; this.style.color='var(--text-secondary)';">
                        <i class="fas fa-arrows-left-right"></i> Toggle View
                    </button>
                </div>
            </div>
        `;
        
        this.addMessage('assistant', approvalHtml);
        
        // Show diff in CENTER PANEL (Monaco editor)
        this.showDiffInEditor(oldCode, newCode);
    }
    
    showDiffInEditor(oldCode, newCode) {
        // Create Monaco diff editor in the center panel
        const editorContainer = document.getElementById('monacoEditor');
        
        // Clear existing editor
        if (this.diffEditor) {
            this.diffEditor.dispose();
        }
        if (this.editor) {
            this.editor.dispose();
        }
        
        editorContainer.innerHTML = '';
        
        // Create diff editor
        this.diffEditor = monaco.editor.createDiffEditor(editorContainer, {
            theme: 'vs-dark',
            automaticLayout: true,
            renderSideBySide: true,
            readOnly: true,
            fontSize: 14,
            minimap: { enabled: false },
            renderOverviewRuler: false
        });
        
        // Set models
        const originalModel = monaco.editor.createModel(oldCode, this.currentFile.language);
        const modifiedModel = monaco.editor.createModel(newCode, this.currentFile.language);
        
        this.diffEditor.setModel({
            original: originalModel,
            modified: modifiedModel
        });
        
        this.isDiffMode = true;
    }
    
    applyChanges() {
        if (!this.pendingChanges) return;
        
        // Restore normal editor and apply new code
        this.restoreNormalEditor();
        this.editor.setValue(this.pendingChanges.newCode);
        
        this.addMessage('assistant', 
            `✅ Changes applied to <strong>${this.pendingChanges.filename}</strong>! ` +
            `Don't forget to save with Ctrl+S or Cmd+S.`
        );
        
        // Highlight that file needs saving
        this.addMessage('assistant', 
            `💾 <strong>Remember to save your changes!</strong> Press Ctrl+S or Cmd+S to save.`
        );
        
        this.pendingChanges = null;
    }
    
    rejectChanges() {
        if (!this.pendingChanges) return;
        
        // Restore normal editor with original code
        this.restoreNormalEditor();
        this.editor.setValue(this.pendingChanges.oldCode);
        
        this.addMessage('assistant', 
            `❌ Changes rejected. Your original code in <strong>${this.pendingChanges.filename}</strong> remains unchanged.`
        );
        
        this.pendingChanges = null;
    }
    
    showSideBySide() {
        if (!this.pendingChanges || !this.diffEditor) return;
        
        // Toggle between side-by-side and inline diff
        const currentMode = this.diffEditor.getOptions().get(monaco.editor.EditorOption.renderSideBySide);
        
        this.diffEditor.updateOptions({
            renderSideBySide: !currentMode
        });
        
        const mode = !currentMode ? 'side-by-side' : 'inline';
        this.addMessage('assistant', `🔄 Diff view changed to <strong>${mode}</strong> mode.`);
    }
    
    restoreNormalEditor() {
        // Dispose diff editor if it exists
        if (this.diffEditor) {
            this.diffEditor.dispose();
            this.diffEditor = null;
        }
        
        // Recreate normal editor
        const editorContainer = document.getElementById('monacoEditor');
        editorContainer.innerHTML = '';
        
        this.editor = monaco.editor.create(editorContainer, {
            value: '',
            language: this.currentFile.language || 'python',
            theme: 'vs-dark',
            automaticLayout: true,
            fontSize: 14,
            minimap: { enabled: true },
            scrollBeyondLastLine: false,
            renderWhitespace: 'selection',
            tabSize: 4,
        });
        
        // Re-add save command
        this.editor.addCommand(monaco.KeyMod.CtrlCmd | monaco.KeyCode.KeyS, () => {
            this.saveCurrentFile();
        });
        
        this.isDiffMode = false;
    }
    
    isCodeGenerationRequest(text) {
        // Determine if user wants code generation or just an explanation/question
        const lowerText = text.toLowerCase();
        
        // Code generation keywords
        const codeKeywords = [
            'create', 'make', 'build', 'write', 'generate', 'add', 'implement',
            'develop', 'code', 'function', 'class', 'module', 'script',
            'refactor', 'fix bug', 'modify', 'update', 'change', 'edit',
            'insert', 'append', 'prepend'
        ];
        
        // Question/explanation keywords
        const questionKeywords = [
            'explain', 'what is', 'what does', 'how does', 'why',
            'can you explain', 'tell me', 'describe', 'what are',
            'help me understand', 'show me how', 'teach me',
            'documentation', 'docs', 'meaning'
        ];
        
        // Check for question patterns first (they take precedence)
        const hasQuestionMark = lowerText.includes('?');
        const startsWithQuestion = /^(what|why|how|when|where|who|which|can you|could you|would you|do you|does it|is it|are there)\b/.test(lowerText);
        const hasQuestionKeyword = questionKeywords.some(kw => lowerText.includes(kw));
        
        if (hasQuestionMark || startsWithQuestion || hasQuestionKeyword) {
            // Even if it has code keywords, if it's a question, treat as explanation request
            return false;
        }
        
        // Check for code generation keywords
        const hasCodeKeyword = codeKeywords.some(kw => lowerText.includes(kw));
        
        return hasCodeKeyword;
    }
    
    async analyzeCodebase() {
        this.addMessage('assistant', 
            `<div style="padding: 15px; background: linear-gradient(135deg, rgba(78, 201, 176, 0.1), rgba(0, 122, 204, 0.1)); border-radius: 8px; border-left: 3px solid var(--accent-green);">
                <p style="font-weight: bold; margin-bottom: 8px;">🧠 Analyzing Codebase...</p>
                <p style="font-size: 12px; color: var(--text-secondary);">This may take a moment. I'm scanning your files and generating a mental model.</p>
            </div>`
        );
        
        // For external folders, we need to analyze client-side since we can't access them from backend
        if (this.isExternalWorkspace && this.externalFiles) {
            // Gather file info from client-side
            const fileInfo = {
                files: [],
                totalFiles: this.externalFiles.size,
                folderName: this.activeWorkspacePath
            };
            
            // Collect file paths and basic info
            for (let [path, file] of this.externalFiles) {
                fileInfo.files.push({
                    path: path,
                    name: file.name,
                    size: file.size,
                    extension: '.' + file.name.split('.').pop().toLowerCase()
                });
            }
            
            // Request analysis with external folder data
            this.socket.emit('analyze_codebase', {
                isExternal: true,
                fileInfo: fileInfo
            });
        } else {
            // Request analysis from backend for workspace folder
            this.socket.emit('analyze_codebase', {
                isExternal: false
            });
        }
    }
    
    showExternalFileCreationDialog(filename, code, language) {
        // Show the code in the editor first
        this.editor.setValue(code);
        monaco.editor.setModelLanguage(this.editor.getModel(), language);
        
        // Show editor
        document.getElementById('welcomeScreen').style.display = 'none';
        document.getElementById('editorContainer').style.display = 'block';
        
        // Update current file
        this.currentFile = {
            path: filename,
            language: language,
            content: code,
            isExternal: true,
            isUnsaved: true
        };
        
        // Update tab
        this.updateTab(filename);
        
        // Show save options
        this.addMessage('assistant', 
            `<div style="padding: 15px; background: rgba(0, 122, 204, 0.1); border-radius: 8px; border: 2px solid var(--accent-blue);">
                <p style="font-weight: bold; color: var(--accent-blue); margin-bottom: 10px;">💾 Save Generated File</p>
                <p style="margin-bottom: 15px; font-size: 13px;">Since you're working with an external folder, I've opened the code in the editor. Choose how to save it:</p>
                <div style="display: flex; flex-direction: column; gap: 8px;">
                    <button onclick="window.ideInstance.downloadFile('${filename}')" style="
                        padding: 10px 14px; 
                        background: rgba(78, 201, 176, 0.15); 
                        border: 1.5px solid rgba(78, 201, 176, 0.4); 
                        border-radius: 6px; 
                        color: #4ec9b0; 
                        font-weight: 600; 
                        cursor: pointer; 
                        font-size: 13px;
                        display: flex;
                        align-items: center;
                        gap: 6px;
                    " onmouseover="this.style.background='rgba(78, 201, 176, 0.25)';" onmouseout="this.style.background='rgba(78, 201, 176, 0.15)';">
                        <i class="fas fa-download"></i> Download as ${filename}
                    </button>
                    <button onclick="window.ideInstance.copyToClipboard()" style="
                        padding: 10px 14px; 
                        background: rgba(0, 122, 204, 0.15); 
                        border: 1.5px solid rgba(0, 122, 204, 0.4); 
                        border-radius: 6px; 
                        color: #007acc; 
                        font-weight: 600; 
                        cursor: pointer; 
                        font-size: 13px;
                        display: flex;
                        align-items: center;
                        gap: 6px;
                    " onmouseover="this.style.background='rgba(0, 122, 204, 0.25)';" onmouseout="this.style.background='rgba(0, 122, 204, 0.15)';">
                        <i class="fas fa-copy"></i> Copy to Clipboard
                    </button>
                </div>
                <p style="margin-top: 10px; font-size: 11px; color: var(--text-secondary); font-style: italic;">💡 Tip: After downloading, manually place it in your project folder</p>
            </div>`
        );
    }
    
    downloadFile(filename) {
        const content = this.editor.getValue();
        const blob = new Blob([content], { type: 'text/plain' });
        const url = URL.createObjectURL(blob);
        const a = document.createElement('a');
        a.href = url;
        a.download = filename;
        a.click();
        URL.revokeObjectURL(url);
        
        this.addMessage('assistant', `✅ File <strong>${filename}</strong> downloaded! Place it in your project folder.`);
    }
    
    async copyToClipboard() {
        const content = this.editor.getValue();
        try {
            await navigator.clipboard.writeText(content);
            this.addMessage('assistant', `✅ Code copied to clipboard! You can paste it into your project.`);
        } catch (err) {
            this.addMessage('assistant', `❌ Failed to copy to clipboard. Please select and copy manually.`);
        }
    }
    
    async createAnalysisFile(analysisContent, fileCount, languageDistribution) {
        const filename = 'CODEBASE_MENTAL_MODEL.md';
        
        // Add metadata header
        const header = `# Codebase Mental Model\n\n**Generated:** ${new Date().toLocaleString()}  \n**Files Analyzed:** ${fileCount}  \n**Languages:** ${Object.entries(languageDistribution).map(([ext, count]) => `${ext} (${count})`).join(', ')}\n\n---\n\n`;
        
        const fullContent = header + analysisContent;
        
        // Always show in editor first for review (human-in-the-loop)
        this.editor.setValue(fullContent);
        monaco.editor.setModelLanguage(this.editor.getModel(), 'markdown');
        
        document.getElementById('welcomeScreen').style.display = 'none';
        document.getElementById('editorContainer').style.display = 'block';
        
        // Store for later use
        this.pendingAnalysis = {
            filename: filename,
            content: fullContent,
            fileCount: fileCount,
            languageDistribution: languageDistribution
        };
        
        this.currentFile = {
            path: filename,
            language: 'markdown',
            content: fullContent,
            isExternal: this.isExternalWorkspace,
            isUnsaved: true,
            isPendingApproval: true
        };
        
        this.updateTab(filename + ' *');
        
        // For external workspaces, offer download
        if (this.isExternalWorkspace) {
            this.addMessage('assistant', 
                `<div style="padding: 15px; background: rgba(78, 201, 176, 0.1); border-radius: 8px; border: 2px solid var(--accent-green);">
                    <p style="font-weight: bold; color: var(--accent-green); margin-bottom: 10px;">✅ Analysis Complete!</p>
                    <p style="margin-bottom: 10px; font-size: 13px;">I've opened the mental model in the editor for your review.</p>
                    <div style="padding: 12px; background: rgba(255, 193, 7, 0.1); border-left: 3px solid #ffc107; border-radius: 6px; margin-bottom: 12px;">
                        <p style="font-size: 12px; color: #ffc107; margin: 0;">⚠️ <strong>Human-in-the-Loop:</strong> Please review the analysis before saving.</p>
                    </div>
                    <button onclick="window.ideInstance.downloadFile('${filename}')" style="
                        padding: 10px 14px; 
                        background: rgba(78, 201, 176, 0.15); 
                        border: 1.5px solid rgba(78, 201, 176, 0.4); 
                        border-radius: 6px; 
                        color: #4ec9b0; 
                        font-weight: 600; 
                        cursor: pointer; 
                        font-size: 13px;
                        display: flex;
                        align-items: center;
                        gap: 6px;
                    " onmouseover="this.style.background='rgba(78, 201, 176, 0.25)';" onmouseout="this.style.background='rgba(78, 201, 176, 0.15)';">
                        <i class="fas fa-download"></i> Download ${filename}
                    </button>
                    <p style="margin-top: 10px; font-size: 11px; color: var(--text-secondary); font-style: italic;">💡 Place it in your project's root directory after review</p>
                </div>`
            );
        } else {
            // For workspace folders, show approval dialog
            this.addMessage('assistant', 
                `<div style="padding: 15px; background: rgba(78, 201, 176, 0.1); border-radius: 8px; border: 2px solid var(--accent-green);">
                    <p style="font-weight: bold; color: var(--accent-green); margin-bottom: 10px;">✅ Analysis Complete!</p>
                    <p style="margin-bottom: 10px; font-size: 13px;">I've opened the mental model in the editor for your review.</p>
                    <div style="padding: 12px; background: rgba(255, 193, 7, 0.1); border-left: 3px solid #ffc107; border-radius: 6px; margin-bottom: 12px;">
                        <p style="font-size: 12px; color: #ffc107; margin: 0;">⚠️ <strong>Human-in-the-Loop:</strong> Please review the analysis before saving to your workspace.</p>
                    </div>
                    <div style="display: flex; gap: 10px; flex-wrap: wrap;">
                        <button onclick="window.ideInstance.approveAndSaveAnalysis()" style="
                            padding: 10px 16px; 
                            background: rgba(78, 201, 176, 0.2); 
                            border: 1.5px solid rgba(78, 201, 176, 0.5); 
                            border-radius: 6px; 
                            color: #4ec9b0; 
                            font-weight: 600; 
                            cursor: pointer; 
                            font-size: 13px;
                            display: flex;
                            align-items: center;
                            gap: 6px;
                        " onmouseover="this.style.background='rgba(78, 201, 176, 0.3)';" onmouseout="this.style.background='rgba(78, 201, 176, 0.2)';">
                            <i class="fas fa-check"></i> Approve & Save to Workspace
                        </button>
                        <button onclick="window.ideInstance.rejectAnalysis()" style="
                            padding: 10px 16px; 
                            background: rgba(255, 75, 75, 0.15); 
                            border: 1.5px solid rgba(255, 75, 75, 0.4); 
                            border-radius: 6px; 
                            color: #ff4b4b; 
                            font-weight: 600; 
                            cursor: pointer; 
                            font-size: 13px;
                            display: flex;
                            align-items: center;
                            gap: 6px;
                        " onmouseover="this.style.background='rgba(255, 75, 75, 0.25)';" onmouseout="this.style.background='rgba(255, 75, 75, 0.15)';">
                            <i class="fas fa-times"></i> Discard
                        </button>
                    </div>
                    <p style="margin-top: 10px; font-size: 11px; color: var(--text-secondary); font-style: italic;">💡 You can edit the analysis in the editor before saving</p>
                </div>`
            );
        }
    }
    
    async approveAndSaveAnalysis() {
        if (!this.pendingAnalysis) {
            this.addMessage('assistant', '❌ No pending analysis to save.');
            return;
        }
        
        const { filename, fileCount, languageDistribution } = this.pendingAnalysis;
        const content = this.editor.getValue();  // Get possibly edited content
        
        this.addMessage('assistant', `💾 Saving <strong>${filename}</strong> to workspace...`);
        
        try {
            // Create the file
            const response = await fetch('/api/file/create', {
                method: 'POST',
                headers: { 'Content-Type': 'application/json' },
                body: JSON.stringify({ path: filename })
            });
            
            const result = await response.json();
            
            if (result.success || result.error?.includes('already exists')) {
                // Write the analysis to the file
                const writeResponse = await fetch('/api/file/write', {
                    method: 'POST',
                    headers: { 'Content-Type': 'application/json' },
                    body: JSON.stringify({
                        path: filename,
                        content: content
                    })
                });
                
                const writeResult = await writeResponse.json();
                
                if (writeResult.success) {
                    this.addMessage('assistant', 
                        `✅ <strong>${filename}</strong> saved successfully to your workspace!`
                    );
                    
                    // Clear pending state
                    this.pendingAnalysis = null;
                    this.currentFile.isPendingApproval = false;
                    this.currentFile.isUnsaved = false;
                    this.updateTab(filename);
                    
                    // Refresh file tree to show the new file
                    await this.loadFileTree();
                } else {
                    this.addMessage('assistant', `❌ Failed to save: ${writeResult.error}`);
                }
            } else {
                this.addMessage('assistant', `❌ Failed to create file: ${result.error}`);
            }
        } catch (error) {
            console.error('Failed to save analysis file:', error);
            this.addMessage('assistant', `❌ Failed to save analysis file: ${error.message}`);
        }
    }
    
    rejectAnalysis() {
        if (!this.pendingAnalysis) {
            return;
        }
        
        this.addMessage('assistant', '🗑️ Analysis discarded. The file was not saved.');
        this.pendingAnalysis = null;
        
        // Close the editor or show welcome screen
        document.getElementById('editorContainer').style.display = 'none';
        document.getElementById('welcomeScreen').style.display = 'flex';
        this.currentFile = null;
    }
}

// Initialize the IDE when the page loads
document.addEventListener('DOMContentLoaded', () => {
    const ide = new VoiceFirstIDE();
    // Make it globally accessible for button onclick handlers
    window.ideInstance = ide;
});

// Function to check STT configuration
async function checkSTTConfig() {
    const infoDiv = document.getElementById('sttInfo');
    infoDiv.innerHTML = '<span style="color: var(--accent-blue);">Checking...</span>';
    
    try {
        const response = await fetch('/api/stt/test');
        const data = await response.json();
        
        if (data.success) {
            let html = `
                <div style="padding: 10px; background: var(--bg-tertiary); border-radius: 4px; border-left: 3px solid var(--accent-green);">
                    <p style="margin-bottom: 5px; color: var(--accent-green); font-weight: bold;">✅ STT Configured</p>
                    <p style="margin-bottom: 3px;"><strong>Name:</strong> ${data.stt_name}</p>
                    <p style="margin-bottom: 3px;"><strong>Description:</strong> ${data.stt_description}</p>
                    <p><strong>Status:</strong> <span style="color: var(--success);">Working</span></p>
            `;
            
            if (data.metadata && data.metadata.source) {
                const sourceDisplay = {
                    'web_speech_api': '🌐 Web Speech API (Browser)',
                    'google_stt_enhanced': '☁️ Google Cloud STT (SOTA)',
                    'text_passthrough': '📝 Text passthrough'
                };
                html += `<p><strong>Current Source:</strong> ${sourceDisplay[data.metadata.source] || data.metadata.source}</p>`;
            }
            
            html += '</div>';
            infoDiv.innerHTML = html;
        } else {
            infoDiv.innerHTML = `<p style="color: var(--error);">❌ Error: ${data.error}</p>`;
        }
    } catch (error) {
        infoDiv.innerHTML = `<p style="color: var(--error);">❌ Failed to check STT: ${error.message}</p>`;
    }
}
