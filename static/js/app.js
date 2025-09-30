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
                this.createAndShowNewFile(data.code, data.language);
            }
        });
        
        this.socket.on('pipeline_complete', (data) => {
            this.addMessage('assistant', '🎉 Pipeline complete! Code is ready.');
            setTimeout(() => this.resetAgentStatus(), 3000);
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
    }
    
    async startRecording() {
        try {
            // Use Web Speech API (built into Chrome/Edge)
            if (!('webkitSpeechRecognition' in window) && !('SpeechRecognition' in window)) {
                this.addMessage('assistant', 
                    '❌ Speech recognition not supported in this browser. ' +
                    'Please use Chrome, Edge, or Safari, or type your command instead.'
                );
                return;
            }
            
            const SpeechRecognition = window.SpeechRecognition || window.webkitSpeechRecognition;
            this.recognition = new SpeechRecognition();
            
            this.recognition.continuous = false;
            this.recognition.interimResults = false;
            this.recognition.lang = 'en-US';
            
            this.recognition.onstart = () => {
                this.isRecording = true;
                document.getElementById('micButton').classList.add('recording');
                this.addMessage('assistant', '🎤 Listening... Speak your command now.');
            };
            
            this.recognition.onresult = (event) => {
                const transcript = event.results[0][0].transcript;
                const confidence = event.results[0][0].confidence;
                
                this.addMessage('user', transcript);
                this.addMessage('assistant', 
                    `Heard: "${transcript}" (confidence: ${Math.round(confidence * 100)}%)`
                );
                
                // Send to backend
                this.processVoiceCommand(transcript);
            };
            
            this.recognition.onerror = (event) => {
                console.error('Speech recognition error:', event.error);
                this.isRecording = false;
                document.getElementById('micButton').classList.remove('recording');
                
                let errorMsg = 'Speech recognition error: ';
                switch(event.error) {
                    case 'no-speech':
                        errorMsg += 'No speech detected. Please try again.';
                        break;
                    case 'audio-capture':
                        errorMsg += 'No microphone found. Please check your audio settings.';
                        break;
                    case 'not-allowed':
                        errorMsg += 'Microphone permission denied. Please allow microphone access.';
                        break;
                    default:
                        errorMsg += event.error;
                }
                this.addMessage('assistant', `❌ ${errorMsg}`);
            };
            
            this.recognition.onend = () => {
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
            this.recognition.stop();
            this.isRecording = false;
            document.getElementById('micButton').classList.remove('recording');
        }
    }
    
    processVoiceCommand(transcript) {
        // Get current file context if available
        const context = {};
        if (this.currentFile) {
            context.current_file = this.currentFile.path;
            context.language = this.currentFile.language;
            context.file_content = this.editor.getValue();
        }
        
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
        
        // Get current file context if available
        const context = {};
        if (this.currentFile) {
            context.current_file = this.currentFile.path;
            context.language = this.currentFile.language;
            context.file_content = this.editor.getValue();
        }
        
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
        
        // Render the tree
        this.renderFileTree(fileTree);
        
        this.addMessage('assistant', `✅ Loaded ${files.length} files from external folder!`);
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
    
    async createAndShowNewFile(code, language) {
        // Generate filename based on language and timestamp
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
        const filename = `generated_${timestamp}.${ext}`;
        
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
            <div style="margin-top: 15px; padding: 20px; background: var(--bg-tertiary); border-radius: 8px; border: 2px solid var(--accent-blue);">
                <p style="margin-bottom: 10px; font-weight: bold; color: var(--accent-blue); font-size: 14px;">⚠️ Review Required</p>
                <p style="margin-bottom: 20px; font-size: 13px; line-height: 1.6;">The AI wants to modify <strong>${filename}</strong>.<br>Review the changes in the <strong>center editor</strong> (red = removed, green = added)</p>
                <div style="display: flex; flex-direction: column; gap: 10px;">
                    <button onclick="window.ideInstance.applyChanges()" style="width: 100%; padding: 12px; background: linear-gradient(135deg, #4ec9b0, #89d185); border: none; border-radius: 6px; color: white; font-weight: bold; cursor: pointer; font-size: 14px;">
                        ✅ Apply Changes
                    </button>
                    <button onclick="window.ideInstance.rejectChanges()" style="width: 100%; padding: 12px; background: linear-gradient(135deg, #f48771, #e5c07b); border: none; border-radius: 6px; color: white; font-weight: bold; cursor: pointer; font-size: 14px;">
                        ❌ Reject Changes
                    </button>
                    <button onclick="window.ideInstance.showSideBySide()" style="width: 100%; padding: 12px; background: var(--bg-input); border: 1px solid var(--border-color); border-radius: 6px; color: var(--text-primary); cursor: pointer; font-size: 13px;">
                        🔄 Toggle Side-by-Side
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
}

// Initialize the IDE when the page loads
document.addEventListener('DOMContentLoaded', () => {
    const ide = new VoiceFirstIDE();
    // Make it globally accessible for button onclick handlers
    window.ideInstance = ide;
});
