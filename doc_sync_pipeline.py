"""
LangChain-Enabled Cyclic Document Synchronization Pipeline

This module implements a multi-agent system using LangChain and LangGraph
to automatically detect and propagate code changes across all markdown documentation.

Architecture:
- Agent 1: DocumentScannerAgent - Scans repository and scores documentation
- Agent 2: DocumentModifierAgent - Applies changes to markdown files
- Cyclic execution via LangGraph until full synchronization achieved
"""

import os
import re
import ast
from pathlib import Path
from typing import List, Dict, Any, Optional, Tuple
from dataclasses import dataclass

from pydantic import BaseModel, Field
from langchain.agents import Tool, AgentExecutor, create_structured_chat_agent
from langchain.memory import ConversationBufferMemory
from langchain.prompts import ChatPromptTemplate, MessagesPlaceholder
from langchain_openai import ChatOpenAI, OpenAIEmbeddings
from langchain_community.vectorstores import FAISS
from langchain.text_splitter import RecursiveCharacterTextSplitter
from langchain.docstore.document import Document
from langgraph.graph import StateGraph, END
from langchain.tools import BaseTool
from langchain.callbacks.manager import CallbackManagerForToolRun


# ==============================================================================
# PYDANTIC STRUCTURED OUTPUT MODELS
# ==============================================================================

class RenamedMethod(BaseModel):
    """Model for renamed method information"""
    class_name: str = Field(description="Class containing the method")
    old_name: str = Field(description="Original method name")
    new_name: str = Field(description="New method name")
    method_type: str = Field(description="Method type: class_method, instance_method, function")


class FileChangeScore(BaseModel):
    """Model for file change necessity scoring"""
    file_path: str = Field(description="Path to the markdown file")
    score: float = Field(description="Change necessity score 0.0-1.0")
    reason: str = Field(description="Reason for the score")
    occurrences_found: int = Field(description="Number of references found")
    patterns_matched: List[str] = Field(description="Patterns that matched")


class DocumentScanReport(BaseModel):
    """Structured output from DocumentScannerAgent"""
    files_scanned: List[str] = Field(description="List of all markdown files scanned")
    change_plan: List[Dict[str, Any]] = Field(description="Detailed change plan per file")
    files_needing_changes: int = Field(description="Number of files requiring changes")
    critical_files_count: int = Field(description="Number of critical files")
    stale_references_found: int = Field(description="Total stale references found")
    documentation_sync_score: float = Field(description="Overall sync score 0.0-1.0")
    method_changes: List[RenamedMethod] = Field(description="Detected method changes")


class DocumentModificationReport(BaseModel):
    """Structured output from DocumentModifierAgent"""
    files_modified: List[str] = Field(description="List of modified files")
    total_replacements: int = Field(description="Total replacements made")
    files_validated: int = Field(description="Number of files validated")
    validation_failures: List[str] = Field(description="Files that failed validation")
    success: bool = Field(description="Whether all modifications succeeded")


class PipelineState(BaseModel):
    """LangGraph state for cyclic execution"""
    iteration: int = Field(default=0, description="Current iteration number")
    scan_report: Optional[DocumentScanReport] = Field(default=None)
    modification_report: Optional[DocumentModificationReport] = Field(default=None)
    is_synchronized: bool = Field(default=False)
    max_iterations: int = Field(default=10)
    repository_path: str = Field(description="Root path of repository")
    method_changes: List[RenamedMethod] = Field(default_factory=list)


# ==============================================================================
# LANGCHAIN TOOLS FOR AGENT 1: DocumentScannerAgent
# ==============================================================================

class RepositoryFileListerTool(BaseTool):
    """Tool to recursively list all markdown files in repository"""
    
    name: str = "list_markdown_files"
    description: str = "Recursively list ALL .md files in the repository. Returns list of file paths."
    repository_path: str = Field(description="Root path of repository")
    
    def __init__(self, repository_path: str):
        super().__init__(repository_path=repository_path)
    
    def _run(
        self,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> Dict[str, List[str]]:
        """Execute the tool"""
        md_files = []
        repo_path = Path(self.repository_path)
        
        # Recursively find all .md files
        for md_file in repo_path.rglob("*.md"):
            # Skip hidden directories and node_modules
            if not any(part.startswith('.') for part in md_file.parts):
                if 'node_modules' not in md_file.parts:
                    md_files.append(str(md_file.relative_to(repo_path)))
        
        return {
            "md_files": sorted(md_files),
            "total_count": len(md_files)
        }


class MarkdownFileReaderTool(BaseTool):
    """Tool to read content of markdown files"""
    
    name: str = "read_markdown_file"
    description: str = "Read the complete content of a markdown file. Input: file_path (str)"
    repository_path: str = Field(description="Root path of repository")
    
    def __init__(self, repository_path: str):
        super().__init__(repository_path=repository_path)
    
    def _run(
        self,
        file_path: str,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> Dict[str, str]:
        """Execute the tool"""
        full_path = Path(self.repository_path) / file_path
        
        if not full_path.exists():
            return {"error": f"File not found: {file_path}", "content": ""}
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                content = f.read()
            return {
                "file_path": file_path,
                "content": content,
                "line_count": len(content.splitlines())
            }
        except Exception as e:
            return {"error": str(e), "content": ""}


class FunctionChangeExtractorTool(BaseTool):
    """Tool to extract function/method changes from Python code"""
    
    name: str = "extract_function_changes"
    description: str = "Extract renamed, modified, or deleted functions/methods from Python files"
    repository_path: str = Field(description="Root path of repository")
    
    def __init__(self, repository_path: str):
        super().__init__(repository_path=repository_path)
    
    def _run(
        self,
        python_file: str = "st3215/st3215.py",
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> Dict[str, List[Dict]]:
        """Execute the tool"""
        full_path = Path(self.repository_path) / python_file
        
        if not full_path.exists():
            return {"renamed_methods": [], "error": "File not found"}
        
        try:
            with open(full_path, 'r', encoding='utf-8') as f:
                tree = ast.parse(f.read())
            
            methods = []
            current_class = None
            
            for node in ast.walk(tree):
                if isinstance(node, ast.ClassDef):
                    current_class = node.name
                elif isinstance(node, ast.FunctionDef):
                    if current_class:
                        methods.append({
                            "class": current_class,
                            "method_name": node.name,
                            "type": "class_method",
                            "line_number": node.lineno
                        })
            
            return {
                "methods_found": methods,
                "total_count": len(methods)
            }
        except Exception as e:
            return {"error": str(e), "renamed_methods": []}


class MarkdownReferenceExtractorTool(BaseTool):
    """Tool to find all occurrences of function names in markdown files"""
    
    name: str = "find_markdown_references"
    description: str = "Find ALL occurrences of a function/method name in markdown content. Input: method_name (str), file_content (str)"
    
    name: str = "find_markdown_references"
    
    def _run(
        self,
        method_name: str,
        file_content: str,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> Dict[str, Any]:
        """Execute the tool"""
        patterns = [
            rf'\b{method_name}\(',           # FunctionName(
            rf'\.{method_name}\(',            # .FunctionName(
            rf'##\s+{method_name}',          # ## FunctionName
            rf'###\s+{method_name}',         # ### FunctionName
            rf'`{method_name}`',              # `FunctionName`
            rf'\|\s*{method_name}\s*\|',     # | FunctionName |
            rf'\b{method_name}\b(?!\w)',     # Standalone word
        ]
        
        occurrences = []
        lines = file_content.splitlines()
        
        for pattern in patterns:
            regex = re.compile(pattern, re.MULTILINE)
            for match in regex.finditer(file_content):
                line_num = file_content[:match.start()].count('\n') + 1
                occurrences.append({
                    "line": line_num,
                    "pattern": pattern,
                    "match": match.group(),
                    "context": lines[line_num - 1] if line_num <= len(lines) else ""
                })
        
        return {
            "method_name": method_name,
            "occurrences": occurrences,
            "total_count": len(occurrences),
            "patterns_matched": list(set(occ["pattern"] for occ in occurrences))
        }


class DocumentationScoringTool(BaseTool):
    """Tool to assign change necessity score to files"""
    
    name: str = "score_documentation_file"
    description: str = "Assign a change necessity score (0.0-1.0) to a markdown file based on references found"
    
    def _run(
        self,
        file_path: str,
        occurrences_count: int,
        has_heading_reference: bool = False,
        has_api_section: bool = False,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> Dict[str, Any]:
        """Execute the tool"""
        score = 0.0
        reasons = []
        
        # Base score from occurrence count
        if occurrences_count > 0:
            score += min(0.5, occurrences_count * 0.05)
            reasons.append(f"{occurrences_count} references found")
        
        # Boost for heading references
        if has_heading_reference:
            score += 0.3
            reasons.append("Method appears in headings")
        
        # Boost for API section
        if has_api_section:
            score += 0.2
            reasons.append("File contains API documentation")
        
        # Normalize score
        score = min(1.0, score)
        
        # Determine criticality
        is_critical = score > 0.7
        
        return {
            "file_path": file_path,
            "score": score,
            "is_critical": is_critical,
            "reason": "; ".join(reasons) if reasons else "No references found",
            "occurrences_count": occurrences_count
        }


class RepositorySearchTool(BaseTool):
    """Tool for semantic and exact search using FAISS vector store"""
    
    name: str = "search_repository"
    description: str = "Perform semantic and exact search across markdown files"
    vectorstore: Optional[FAISS] = Field(default=None)
    documents: List[Document] = Field(default_factory=list)
    repository_path: str = Field(description="Root path of repository")
    
    def __init__(self, repository_path: str):
        super().__init__(repository_path=repository_path)
        self._initialize_vectorstore()
    
    def _initialize_vectorstore(self):
        """Initialize FAISS vectorstore with markdown documents"""
        repo_path = Path(self.repository_path)
        md_files = list(repo_path.rglob("*.md"))
        
        documents = []
        for md_file in md_files:
            if not any(part.startswith('.') for part in md_file.parts):
                try:
                    with open(md_file, 'r', encoding='utf-8') as f:
                        content = f.read()
                    
                    doc = Document(
                        page_content=content,
                        metadata={"source": str(md_file.relative_to(repo_path))}
                    )
                    documents.append(doc)
                except Exception:
                    continue
        
        if documents:
            text_splitter = RecursiveCharacterTextSplitter(
                chunk_size=1000,
                chunk_overlap=200
            )
            split_docs = text_splitter.split_documents(documents)
            
            try:
                embeddings = OpenAIEmbeddings()
                self.vectorstore = FAISS.from_documents(split_docs, embeddings)
                self.documents = documents
            except Exception:
                # Fallback if OpenAI not configured
                self.vectorstore = None
                self.documents = documents
    
    def _run(
        self,
        query: str,
        search_type: str = "similarity",
        k: int = 5,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> Dict[str, Any]:
        """Execute the tool"""
        results = []
        
        if search_type == "similarity" and self.vectorstore:
            # Semantic search
            docs = self.vectorstore.similarity_search(query, k=k)
            results = [
                {
                    "source": doc.metadata.get("source", "unknown"),
                    "content": doc.page_content[:200],
                    "search_type": "semantic"
                }
                for doc in docs
            ]
        else:
            # Exact match search
            for doc in self.documents:
                if query.lower() in doc.page_content.lower():
                    results.append({
                        "source": doc.metadata.get("source", "unknown"),
                        "content": doc.page_content[:200],
                        "search_type": "exact"
                    })
        
        return {
            "query": query,
            "results": results[:k],
            "total_found": len(results)
        }


# ==============================================================================
# LANGCHAIN TOOLS FOR AGENT 2: DocumentModifierAgent
# ==============================================================================

class MarkdownFileWriterTool(BaseTool):
    """Tool to write content to markdown files"""
    
    name: str = "write_markdown_file"
    description: str = "Write content to a markdown file. Input: file_path (str), content (str)"
    repository_path: str = Field(description="Root path of repository")
    
    def __init__(self, repository_path: str):
        super().__init__(repository_path=repository_path)
    
    def _run(
        self,
        file_path: str,
        content: str,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> Dict[str, Any]:
        """Execute the tool"""
        full_path = Path(self.repository_path) / file_path
        
        try:
            # Backup original
            backup_path = full_path.with_suffix('.md.bak')
            if full_path.exists():
                with open(full_path, 'r', encoding='utf-8') as f:
                    original = f.read()
                with open(backup_path, 'w', encoding='utf-8') as f:
                    f.write(original)
            
            # Write new content
            with open(full_path, 'w', encoding='utf-8') as f:
                f.write(content)
            
            return {
                "success": True,
                "file_path": file_path,
                "bytes_written": len(content.encode('utf-8')),
                "backup_created": str(backup_path)
            }
        except Exception as e:
            return {
                "success": False,
                "error": str(e),
                "file_path": file_path
            }


class ReferenceReplacementTool(BaseTool):
    """Tool to replace all stale references in markdown content"""
    
    name: str = "replace_references"
    description: str = "Replace ALL occurrences of old method name with new name. Input: content (str), old_name (str), new_name (str)"
    
    def _run(
        self,
        content: str,
        old_name: str,
        new_name: str,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> Dict[str, Any]:
        """Execute the tool"""
        replacements = []
        new_content = content
        
        # Define replacement patterns
        patterns = [
            # Method calls: PingServo( -> LinkServo(
            (rf'\b{old_name}\(', f'{new_name}('),
            # Instance calls: .PingServo( -> .LinkServo(
            (rf'\.{old_name}\(', f'.{new_name}('),
            # Headings: ### PingServo -> ### LinkServo
            (rf'(###+\s+){old_name}\b', rf'\1{new_name}'),
            # Inline code: `PingServo` -> `LinkServo`
            (rf'`{old_name}`', f'`{new_name}`'),
            # Table entries: | PingServo | -> | LinkServo |
            (rf'\|\s*{old_name}\s*\|', f'| {new_name} |'),
            # Standalone mentions: PingServo -> LinkServo (word boundary)
            (rf'\b{old_name}\b(?!\()', new_name),
        ]
        
        total_replacements = 0
        for pattern, replacement in patterns:
            regex = re.compile(pattern, re.MULTILINE)
            matches = list(regex.finditer(new_content))
            
            if matches:
                new_content = regex.sub(replacement, new_content)
                total_replacements += len(matches)
                replacements.append({
                    "pattern": pattern,
                    "count": len(matches)
                })
        
        return {
            "new_content": new_content,
            "total_replacements": total_replacements,
            "replacements_by_pattern": replacements,
            "content_changed": new_content != content
        }


class DocumentValidationTool(BaseTool):
    """Tool to validate that file has no stale references"""
    
    name: str = "validate_document"
    description: str = "Verify file contains ZERO stale references. Input: content (str), old_name (str)"
    
    def _run(
        self,
        content: str,
        old_name: str,
        run_manager: Optional[CallbackManagerForToolRun] = None
    ) -> Dict[str, Any]:
        """Execute the tool"""
        # Search for any remaining occurrences
        patterns = [
            rf'\b{old_name}\(',
            rf'\.{old_name}\(',
            rf'##\s+{old_name}',
            rf'###\s+{old_name}',
            rf'`{old_name}`',
            rf'\b{old_name}\b'
        ]
        
        violations = []
        for pattern in patterns:
            regex = re.compile(pattern, re.MULTILINE)
            matches = list(regex.finditer(content))
            
            if matches:
                for match in matches:
                    line_num = content[:match.start()].count('\n') + 1
                    violations.append({
                        "line": line_num,
                        "pattern": pattern,
                        "match": match.group()
                    })
        
        is_valid = len(violations) == 0
        
        return {
            "is_valid": is_valid,
            "stale_references_found": len(violations),
            "violations": violations,
            "old_name": old_name
        }


# ==============================================================================
# LANGCHAIN AGENTS
# ==============================================================================

class DocumentScannerAgent:
    """Agent 1: Scans repository and produces change plan"""
    
    def __init__(self, repository_path: str, method_changes: List[RenamedMethod]):
        self.repository_path = repository_path
        self.method_changes = method_changes
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0  # Deterministic
        )
        
        # Initialize tools
        self.tools = [
            RepositoryFileListerTool(repository_path),
            MarkdownFileReaderTool(repository_path),
            FunctionChangeExtractorTool(repository_path),
            MarkdownReferenceExtractorTool(),
            DocumentationScoringTool(),
            RepositorySearchTool(repository_path)
        ]
        
        # Initialize memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
    
    def scan_repository(self) -> DocumentScanReport:
        """Execute scanning process"""
        # List all markdown files
        lister = RepositoryFileListerTool(self.repository_path)
        md_files_result = lister._run()
        md_files = md_files_result["md_files"]
        
        # Scan each file for references
        reader = MarkdownFileReaderTool(self.repository_path)
        reference_finder = MarkdownReferenceExtractorTool()
        scorer = DocumentationScoringTool()
        
        change_plan = []
        total_stale_references = 0
        critical_files = 0
        files_needing_changes = 0
        
        for method_change in self.method_changes:
            old_name = method_change.old_name
            new_name = method_change.new_name
            
            for md_file in md_files:
                # Read file
                file_result = reader._run(md_file)
                if "error" in file_result:
                    continue
                
                content = file_result["content"]
                
                # Find references
                ref_result = reference_finder._run(old_name, content)
                occurrences = ref_result["total_count"]
                
                if occurrences > 0:
                    # Score file
                    has_heading = any("##" in occ["pattern"] for occ in ref_result["occurrences"])
                    has_api = "API" in content or "api" in md_file.lower()
                    
                    score_result = scorer._run(
                        md_file,
                        occurrences,
                        has_heading,
                        has_api
                    )
                    
                    change_plan.append({
                        "file": md_file,
                        "old_name": old_name,
                        "new_name": new_name,
                        "occurrences": occurrences,
                        "score": score_result["score"],
                        "is_critical": score_result["is_critical"],
                        "reason": score_result["reason"]
                    })
                    
                    total_stale_references += occurrences
                    files_needing_changes += 1
                    
                    if score_result["is_critical"]:
                        critical_files += 1
        
        # Calculate sync score
        if len(md_files) > 0:
            sync_score = 1.0 - (files_needing_changes / len(md_files))
        else:
            sync_score = 1.0
        
        return DocumentScanReport(
            files_scanned=md_files,
            change_plan=change_plan,
            files_needing_changes=files_needing_changes,
            critical_files_count=critical_files,
            stale_references_found=total_stale_references,
            documentation_sync_score=sync_score,
            method_changes=self.method_changes
        )


class DocumentModifierAgent:
    """Agent 2: Applies changes to markdown files"""
    
    def __init__(self, repository_path: str, scan_report: DocumentScanReport):
        self.repository_path = repository_path
        self.scan_report = scan_report
        
        # Initialize LLM
        self.llm = ChatOpenAI(
            model="gpt-4",
            temperature=0
        )
        
        # Initialize tools
        self.tools = [
            MarkdownFileReaderTool(repository_path),
            MarkdownFileWriterTool(repository_path),
            ReferenceReplacementTool(),
            DocumentValidationTool()
        ]
        
        # Initialize memory
        self.memory = ConversationBufferMemory(
            memory_key="chat_history",
            return_messages=True
        )
    
    def apply_changes(self) -> DocumentModificationReport:
        """Execute modification process"""
        reader = MarkdownFileReaderTool(self.repository_path)
        writer = MarkdownFileWriterTool(self.repository_path)
        replacer = ReferenceReplacementTool()
        validator = DocumentValidationTool()
        
        files_modified = []
        total_replacements = 0
        validation_failures = []
        
        # Group changes by file
        file_changes = {}
        for change in self.scan_report.change_plan:
            file_path = change["file"]
            if file_path not in file_changes:
                file_changes[file_path] = []
            file_changes[file_path].append(change)
        
        # Process each file
        for file_path, changes in file_changes.items():
            # Read file
            file_result = reader._run(file_path)
            if "error" in file_result:
                validation_failures.append(file_path)
                continue
            
            content = file_result["content"]
            
            # Apply all replacements for this file
            for change in changes:
                old_name = change["old_name"]
                new_name = change["new_name"]
                
                replace_result = replacer._run(content, old_name, new_name)
                content = replace_result["new_content"]
                total_replacements += replace_result["total_replacements"]
            
            # Write modified content
            write_result = writer._run(file_path, content)
            if not write_result["success"]:
                validation_failures.append(file_path)
                continue
            
            # Validate
            valid = True
            for change in changes:
                validation_result = validator._run(content, change["old_name"])
                if not validation_result["is_valid"]:
                    validation_failures.append(file_path)
                    valid = False
                    break
            
            if valid:
                files_modified.append(file_path)
        
        return DocumentModificationReport(
            files_modified=files_modified,
            total_replacements=total_replacements,
            files_validated=len(files_modified),
            validation_failures=validation_failures,
            success=len(validation_failures) == 0
        )


# ==============================================================================
# LANGGRAPH CYCLIC EXECUTION
# ==============================================================================

def create_documentation_sync_graph(
    repository_path: str,
    method_changes: List[RenamedMethod],
    max_iterations: int = 10
) -> StateGraph:
    """Create LangGraph StateGraph for cyclic execution"""
    
    # Define state graph
    workflow = StateGraph(PipelineState)
    
    def scanner_node(state: PipelineState) -> PipelineState:
        """Execute DocumentScannerAgent"""
        agent = DocumentScannerAgent(state.repository_path, state.method_changes)
        scan_report = agent.scan_repository()
        
        state.scan_report = scan_report
        state.iteration += 1
        
        # Check if synchronized
        if (scan_report.stale_references_found == 0 and
            scan_report.files_needing_changes == 0 and
            scan_report.documentation_sync_score == 1.0):
            state.is_synchronized = True
        
        return state
    
    def modifier_node(state: PipelineState) -> PipelineState:
        """Execute DocumentModifierAgent"""
        if state.scan_report is None:
            return state
        
        agent = DocumentModifierAgent(state.repository_path, state.scan_report)
        modification_report = agent.apply_changes()
        
        state.modification_report = modification_report
        
        return state
    
    def should_continue(state: PipelineState) -> str:
        """Determine if cycle should continue"""
        if state.is_synchronized:
            return "end"
        if state.iteration >= state.max_iterations:
            return "end"
        return "scan"
    
    # Add nodes
    workflow.add_node("scan", scanner_node)
    workflow.add_node("modify", modifier_node)
    
    # Add edges
    workflow.set_entry_point("scan")
    workflow.add_edge("scan", "modify")
    workflow.add_conditional_edges(
        "modify",
        should_continue,
        {
            "scan": "scan",
            "end": END
        }
    )
    
    return workflow


# ==============================================================================
# MAIN PIPELINE EXECUTION
# ==============================================================================

class DocumentationSyncPipeline:
    """Main pipeline orchestrator"""
    
    def __init__(
        self,
        repository_path: str,
        method_changes: List[RenamedMethod],
        max_iterations: int = 10
    ):
        self.repository_path = repository_path
        self.method_changes = method_changes
        self.max_iterations = max_iterations
    
    def execute(self) -> Dict[str, Any]:
        """Execute the full cyclic pipeline"""
        # Create initial state
        initial_state = PipelineState(
            iteration=0,
            repository_path=self.repository_path,
            method_changes=self.method_changes,
            max_iterations=self.max_iterations
        )
        
        # Create and compile graph
        graph = create_documentation_sync_graph(
            self.repository_path,
            self.method_changes,
            self.max_iterations
        )
        app = graph.compile()
        
        # Execute cyclic pipeline
        final_state = app.invoke(initial_state)
        
        # Generate final report
        report = {
            "documentation_sync_status": "COMPLETE" if final_state.is_synchronized else "INCOMPLETE",
            "total_iterations": final_state.iteration,
            "total_files_scanned": len(final_state.scan_report.files_scanned) if final_state.scan_report else 0,
            "total_files_modified": len(final_state.modification_report.files_modified) if final_state.modification_report else 0,
            "stale_references_remaining": final_state.scan_report.stale_references_found if final_state.scan_report else 0,
            "sync_score": final_state.scan_report.documentation_sync_score if final_state.scan_report else 0.0,
            "method_changes_processed": len(self.method_changes),
            "final_scan_report": final_state.scan_report.dict() if final_state.scan_report else None,
            "final_modification_report": final_state.modification_report.dict() if final_state.modification_report else None
        }
        
        return report


# ==============================================================================
# CONVENIENCE FUNCTION
# ==============================================================================

def synchronize_documentation(
    repository_path: str,
    renamed_methods: List[Dict[str, str]],
    max_iterations: int = 10
) -> Dict[str, Any]:
    """
    Convenience function to run documentation synchronization pipeline
    
    Args:
        repository_path: Root path of repository
        renamed_methods: List of dicts with 'class_name', 'old_name', 'new_name'
        max_iterations: Maximum number of scan-modify cycles
    
    Returns:
        Final validation report
    
    Example:
        >>> result = synchronize_documentation(
        ...     repository_path="/path/to/repo",
        ...     renamed_methods=[{
        ...         "class_name": "ST3215",
        ...         "old_name": "PingServo",
        ...         "new_name": "LinkServo"
        ...     }]
        ... )
        >>> print(result["documentation_sync_status"])
        COMPLETE
    """
    # Convert to Pydantic models
    method_changes = [
        RenamedMethod(
            class_name=m["class_name"],
            old_name=m["old_name"],
            new_name=m["new_name"],
            method_type=m.get("method_type", "class_method")
        )
        for m in renamed_methods
    ]
    
    # Create and execute pipeline
    pipeline = DocumentationSyncPipeline(
        repository_path=repository_path,
        method_changes=method_changes,
        max_iterations=max_iterations
    )
    
    return pipeline.execute()


if __name__ == "__main__":
    # Example usage
    import sys
    
    repo_path = sys.argv[1] if len(sys.argv) > 1 else "."
    
    # Example: Sync documentation for PingServo -> LinkServo rename
    result = synchronize_documentation(
        repository_path=repo_path,
        renamed_methods=[
            {
                "class_name": "ST3215",
                "old_name": "PingServo",
                "new_name": "LinkServo",
                "method_type": "class_method"
            }
        ],
        max_iterations=5
    )
    
    print("\n" + "="*80)
    print("DOCUMENTATION SYNCHRONIZATION PIPELINE REPORT")
    print("="*80)
    print(f"Status: {result['documentation_sync_status']}")
    print(f"Total Iterations: {result['total_iterations']}")
    print(f"Files Scanned: {result['total_files_scanned']}")
    print(f"Files Modified: {result['total_files_modified']}")
    print(f"Stale References Remaining: {result['stale_references_remaining']}")
    print(f"Sync Score: {result['sync_score']:.2%}")
    print("="*80)
