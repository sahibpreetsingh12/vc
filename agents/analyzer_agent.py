"""
Analyzer Agent - Analyzes codebase structure and generates documentation.

Provides mental models, architecture overviews, and documentation.
"""

import os
from pathlib import Path
from typing import Any, Dict, Optional, List
from .base import Agent, AgentResult


class AnalyzerAgent(Agent):
    """
    Analyzes codebase to provide understanding and documentation.
    
    Can generate:
    - Mental models / architecture overviews
    - File structure documentation
    - Key component summaries
    """
    
    def __init__(self):
        super().__init__(
            name="Analyzer Agent",
            description="Analyzes codebase structure and generates documentation"
        )
    
    def execute(self, input_data: Any, context: Optional[Dict] = None) -> AgentResult:
        """
        Analyze codebase and generate documentation.
        
        Args:
            input_data: Dict with 'action' (analyze/document) and optional 'path'
            context: Optional context with workspace info
            
        Returns:
            AgentResult with analysis/documentation
        """
        try:
            if not isinstance(input_data, dict):
                return AgentResult(
                    success=False,
                    data=None,
                    error="Invalid input format (expected dict with 'action')"
                )
            
            action = input_data.get("action", "analyze")
            workspace_path = input_data.get("path") or context.get("workspace_path") if context else None
            
            if not workspace_path:
                return AgentResult(
                    success=False,
                    data=None,
                    error="No workspace path provided"
                )
            
            if not self.tools:
                return AgentResult(
                    success=False,
                    data=None,
                    error="No LLM tool configured for analysis"
                )
            
            # Scan codebase
            codebase_info = self._scan_codebase(workspace_path)
            
            # Use LLM to generate analysis
            llm_tool = self.tools[0]
            
            if action == "analyze":
                prompt = self._build_analysis_prompt(codebase_info)
            else:
                prompt = self._build_documentation_prompt(codebase_info)
            
            result = llm_tool.call(prompt)
            
            if not result.success:
                return AgentResult(
                    success=False,
                    data=None,
                    error=f"Analysis failed: {result.error}"
                )
            
            return AgentResult(
                success=True,
                data={
                    "analysis": result.output,
                    "action": action,
                    "file_count": codebase_info['file_count'],
                    "language_distribution": codebase_info['language_distribution']
                },
                metadata={
                    "agent": self.name,
                    "workspace": workspace_path
                }
            )
            
        except Exception as e:
            return AgentResult(
                success=False,
                data=None,
                error=f"Analyzer agent error: {str(e)}"
            )
    
    def _scan_codebase(self, workspace_path: str) -> Dict:
        """Scan codebase to gather structural information."""
        workspace = Path(workspace_path)
        
        if not workspace.exists() or not workspace.is_dir():
            return {
                "file_count": 0,
                "language_distribution": {},
                "file_tree": [],
                "key_files": []
            }
        
        # File extensions to include
        code_extensions = {
            '.py', '.js', '.ts', '.jsx', '.tsx', '.html', '.css', '.scss',
            '.java', '.go', '.rs', '.cpp', '.c', '.h', '.hpp',
            '.md', '.json', '.yaml', '.yml', '.toml', '.xml',
            '.sh', '.bash', '.sql'
        }
        
        files = []
        language_count = {}
        key_files = []
        
        # Common important files
        important_files = {
            'readme.md', 'readme.txt', 'package.json', 'requirements.txt',
            'cargo.toml', 'go.mod', 'pom.xml', 'build.gradle',
            'makefile', 'dockerfile', '.env.example', 'setup.py'
        }
        
        # Scan directory (limit depth to avoid overwhelming)
        max_files = 200
        for root, dirs, filenames in os.walk(workspace):
            # Skip common ignore directories
            dirs[:] = [d for d in dirs if d not in {
                '__pycache__', 'node_modules', '.git', 'venv', 'env',
                'dist', 'build', '.idea', '.vscode', 'target'
            }]
            
            for filename in filenames:
                if len(files) >= max_files:
                    break
                
                file_path = Path(root) / filename
                ext = file_path.suffix.lower()
                
                # Track code files
                if ext in code_extensions:
                    rel_path = file_path.relative_to(workspace)
                    files.append({
                        'path': str(rel_path),
                        'extension': ext,
                        'size': file_path.stat().st_size
                    })
                    
                    # Count by language
                    language_count[ext] = language_count.get(ext, 0) + 1
                
                # Track important files
                if filename.lower() in important_files:
                    key_files.append(str(file_path.relative_to(workspace)))
            
            if len(files) >= max_files:
                break
        
        # Build directory tree (simplified)
        file_tree = self._build_tree_structure(files[:50])  # First 50 files
        
        return {
            "file_count": len(files),
            "language_distribution": language_count,
            "file_tree": file_tree,
            "key_files": key_files
        }
    
    def _build_tree_structure(self, files: List[Dict]) -> List[str]:
        """Build a simple tree representation of files."""
        tree = []
        for file in files:
            tree.append(file['path'])
        return tree
    
    def _build_analysis_prompt(self, codebase_info: Dict) -> str:
        """Build prompt for codebase analysis."""
        return f"""You are an expert software architect. Analyze this codebase and provide a comprehensive mental model.

Codebase Structure:
- Total Files: {codebase_info['file_count']}
- Languages: {', '.join(f"{ext} ({count} files)" for ext, count in sorted(codebase_info['language_distribution'].items(), key=lambda x: -x[1]))}
- Key Files: {', '.join(codebase_info['key_files']) if codebase_info['key_files'] else 'None detected'}

File Structure:
{chr(10).join(codebase_info['file_tree'][:30])}
{"..." if len(codebase_info['file_tree']) > 30 else ""}

Generate a comprehensive mental model document in Markdown format that includes:

1. **Project Overview** - What this project appears to be
2. **Architecture** - High-level architecture and design patterns
3. **Key Components** - Main modules/components and their responsibilities
4. **Technology Stack** - Languages, frameworks, and tools used
5. **File Organization** - How the codebase is structured
6. **Entry Points** - Main files to start understanding the code
7. **Dependencies & Integration** - How components interact
8. **Development Workflow** - Likely dev/build/test processes

Make it clear, concise, and actionable for a developer trying to understand this codebase quickly.
Use markdown headers, bullet points, and code blocks where appropriate."""
    
    def _build_documentation_prompt(self, codebase_info: Dict) -> str:
        """Build prompt for documentation generation."""
        return f"""Generate comprehensive documentation for this codebase.

Codebase Structure:
- Total Files: {codebase_info['file_count']}
- Languages: {', '.join(f"{ext} ({count} files)" for ext, count in sorted(codebase_info['language_distribution'].items(), key=lambda x: -x[1]))}

Create a detailed README-style documentation in Markdown that covers:

1. Project title and description
2. Features and capabilities
3. Installation instructions
4. Usage examples
5. Project structure explanation
6. Contributing guidelines
7. License information (if determinable)

Format it professionally as a proper README.md file."""
