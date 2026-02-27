# LangChain Documentation Synchronization Pipeline

## Overview

This is a **LangChain-enabled cyclic multi-agent pipeline** that automatically detects and propagates code changes across all markdown documentation files in your repository.

### Architecture

The system uses **LangGraph** for cyclic execution with two specialized LangChain agents:

1. **DocumentScannerAgent** - Scans repository, detects changes, scores files
2. **DocumentModifierAgent** - Applies changes to markdown files

The pipeline runs cyclically until all documentation is synchronized with the codebase.

## Features

✅ **LangChain Agents** - Structured agent execution with tool calling  
✅ **LangGraph Cyclic Execution** - Repeats scan-modify cycle until complete  
✅ **Pydantic Structured Outputs** - Type-safe data models  
✅ **LangChain Memory** - Tracks state across iterations  
✅ **Vector Store Retrieval** - FAISS-based semantic search  
✅ **Comprehensive Tools** - 10+ specialized tools for scanning and modification  
✅ **Deterministic Execution** - Temperature = 0 for consistent results

## Installation

```bash
# Install LangChain dependencies
pip install -r doc_sync_requirements.txt

# Set OpenAI API key (required for LLM)
export OPENAI_API_KEY="your-api-key-here"
```

## Quick Start

### Basic Usage

```python
from doc_sync_pipeline import synchronize_documentation

# Synchronize documentation after renaming a method
result = synchronize_documentation(
    repository_path="/path/to/your/repo",
    renamed_methods=[
        {
            "class_name": "ST3215",
            "old_name": "PingServo",
            "new_name": "LinkServo",
            "method_type": "class_method"
        }
    ],
    max_iterations=10
)

print(f"Status: {result['documentation_sync_status']}")
print(f"Files Modified: {result['total_files_modified']}")
print(f"Sync Score: {result['sync_score']:.2%}")
```

### Command Line Usage

```bash
# Run pipeline on current directory
python doc_sync_pipeline.py .

# Run pipeline on specific directory
python doc_sync_pipeline.py /path/to/repo
```

## Architecture Details

### Agent 1: DocumentScannerAgent

**Purpose:** Scan repository and produce change plan

**Tools:**
- `RepositoryFileListerTool` - List all .md files recursively
- `MarkdownFileReaderTool` - Read markdown content
- `FunctionChangeExtractorTool` - Extract method changes from Python AST
- `MarkdownReferenceExtractorTool` - Find all method references
- `DocumentationScoringTool` - Score files by change necessity
- `RepositorySearchTool` - Semantic search with FAISS

**Output:** `DocumentScanReport` with structured change plan

### Agent 2: DocumentModifierAgent

**Purpose:** Apply changes to markdown files

**Tools:**
- `MarkdownFileReaderTool` - Read markdown content
- `MarkdownFileWriterTool` - Write updated content
- `ReferenceReplacementTool` - Replace all stale references
- `DocumentValidationTool` - Verify no stale references remain

**Output:** `DocumentModificationReport` with results

### LangGraph Cyclic Execution

```
START
  ↓
DocumentScannerAgent (scan repository)
  ↓
DocumentModifierAgent (apply changes)
  ↓
Check if synchronized?
  ↓ No (stale refs remain)
DocumentScannerAgent (rescan)
  ↓
(repeat until synchronized)
  ↓ Yes (sync_score = 1.0)
END
```

**Termination Conditions:**
- `stale_references_found == 0`
- `files_needing_changes == 0`
- `documentation_sync_score == 1.0`
- OR `max_iterations` reached

## Pydantic Models

### DocumentScanReport
```python
class DocumentScanReport(BaseModel):
    files_scanned: List[str]
    change_plan: List[Dict[str, Any]]
    files_needing_changes: int
    critical_files_count: int
    stale_references_found: int
    documentation_sync_score: float
    method_changes: List[RenamedMethod]
```

### DocumentModificationReport
```python
class DocumentModificationReport(BaseModel):
    files_modified: List[str]
    total_replacements: int
    files_validated: int
    validation_failures: List[str]
    success: bool
```

## Replacement Coverage

The pipeline replaces **ALL** occurrences including:

- ✅ `PingServo(` - Function calls
- ✅ `.PingServo(` - Instance method calls
- ✅ `### PingServo` - Heading references
- ✅ `` `PingServo` `` - Inline code
- ✅ `| PingServo |` - Table entries
- ✅ `PingServo` - Standalone mentions

## Example Output

```
================================================================================
DOCUMENTATION SYNCHRONIZATION PIPELINE REPORT
================================================================================
Status: COMPLETE
Total Iterations: 2
Files Scanned: 6
Files Modified: 6
Stale References Remaining: 0
Sync Score: 100.00%
================================================================================
```

## Advanced Usage

### Custom Method Changes

```python
from doc_sync_pipeline import DocumentationSyncPipeline, RenamedMethod

# Multiple method renames
method_changes = [
    RenamedMethod(
        class_name="ST3215",
        old_name="PingServo",
        new_name="LinkServo",
        method_type="class_method"
    ),
    RenamedMethod(
        class_name="ST3215",
        old_name="ReadData",
        new_name="FetchData",
        method_type="class_method"
    )
]

# Create pipeline
pipeline = DocumentationSyncPipeline(
    repository_path="/path/to/repo",
    method_changes=method_changes,
    max_iterations=15
)

# Execute
result = pipeline.execute()
```

### Access Detailed Reports

```python
result = synchronize_documentation(
    repository_path=".",
    renamed_methods=[...]
)

# Access scan report
scan_report = result["final_scan_report"]
print(f"Files scanned: {scan_report['files_scanned']}")
print(f"Change plan: {scan_report['change_plan']}")

# Access modification report
mod_report = result["final_modification_report"]
print(f"Files modified: {mod_report['files_modified']}")
print(f"Total replacements: {mod_report['total_replacements']}")
```

## Configuration

### Environment Variables

```bash
# Required
export OPENAI_API_KEY="sk-..."

# Optional: Use different model
export OPENAI_MODEL="gpt-4-turbo"

# Optional: Adjust temperature
export OPENAI_TEMPERATURE="0"
```

### Pipeline Parameters

```python
synchronize_documentation(
    repository_path=".",           # Root path of repository
    renamed_methods=[...],         # List of method changes
    max_iterations=10              # Maximum scan-modify cycles
)
```

## Tool Descriptions

| Tool | Purpose | Agent |
|------|---------|-------|
| `RepositoryFileListerTool` | List all .md files | Scanner |
| `MarkdownFileReaderTool` | Read markdown content | Both |
| `FunctionChangeExtractorTool` | Extract code changes | Scanner |
| `MarkdownReferenceExtractorTool` | Find method references | Scanner |
| `DocumentationScoringTool` | Score change necessity | Scanner |
| `RepositorySearchTool` | Semantic/exact search | Scanner |
| `MarkdownFileWriterTool` | Write markdown files | Modifier |
| `ReferenceReplacementTool` | Replace references | Modifier |
| `DocumentValidationTool` | Validate no stale refs | Modifier |

## Memory Management

The pipeline uses **LangChain ConversationBufferMemory** to track:
- Files already modified
- Changes applied
- Scan results
- Change scores
- Remaining stale references

This prevents redundant operations and enables efficient cyclic execution.

## Validation

Each file is validated after modification:

```python
{
  "is_valid": true,
  "stale_references_found": 0,
  "violations": []
}
```

If validation fails, the file is added to `validation_failures` list.

## Limitations

- Requires OpenAI API key (uses GPT-4)
- Processes markdown files only
- Does not modify Python source files
- May take several minutes for large repositories

## Troubleshooting

### "OpenAI API key not found"
```bash
export OPENAI_API_KEY="your-key-here"
```

### "Module not found: langchain"
```bash
pip install -r doc_sync_requirements.txt
```

### Pipeline not converging
- Increase `max_iterations`
- Check for complex regex patterns
- Verify method names are correct

## Future Enhancements

- [ ] Support for more programming languages
- [ ] GitHub PR integration
- [ ] Real-time documentation watching
- [ ] Multi-repository synchronization
- [ ] Custom LLM backends (Anthropic, local models)

## License

Apache License Version 2.0

## Author

Implemented using LangChain, LangGraph, and OpenAI GPT-4
