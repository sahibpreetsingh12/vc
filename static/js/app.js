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
            
            // Show code preview in conversation
            const previewCode = data.code.substring(0, 500) + (data.code.length > 500 ? '...' : '');
            this.addMessage('assistant', `<pre><code>${this.escapeHtml(previewCode)}</code></pre>`);
            
            // Ask user if they want to insert it
            this.addMessage('assistant', 
                `Would you like to:<br>` +
                `• Insert this code into the current file<br>` +
                `• Create a new file with this code<br>` +
                `• Just review it first`
            );
            
            // Store generated code for potential insertion
            this.lastGeneratedCode = data.code;
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
            const stream = await navigator.mediaDevices.getUserMedia({ audio: true });
            this.mediaRecorder = new MediaRecorder(stream);
            this.audioChunks = [];
            
            this.mediaRecorder.ondataavailable = (event) => {
                this.audioChunks.push(event.data);
            };
            
            this.mediaRecorder.onstop = () => {
                const audioBlob = new Blob(this.audioChunks, { type: 'audio/wav' });
                this.processAudio(audioBlob);
                stream.getTracks().forEach(track => track.stop());
            };
            
            this.mediaRecorder.start();
            this.isRecording = true;
            
            document.getElementById('micButton').classList.add('recording');
            this.addMessage('assistant', '🎤 Recording... Click again to stop.');
        } catch (error) {
            console.error('Microphone access denied:', error);
            this.addMessage('assistant', '❌ Microphone access denied. Please check permissions.');
        }
    }
    
    stopRecording() {
        if (this.mediaRecorder && this.isRecording) {
            this.mediaRecorder.stop();
            this.isRecording = false;
            document.getElementById('micButton').classList.remove('recording');
        }
    }
    
    async processAudio(audioBlob) {
        // For now, we'll use the text input as fallback since audio processing requires backend
        this.addMessage('assistant', 
            'Note: Audio recording captured but backend STT integration needed. ' +
            'Please use text input for now or integrate with your STT API.'
        );
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
}

// Initialize the IDE when the page loads
document.addEventListener('DOMContentLoaded', () => {
    new VoiceFirstIDE();
});