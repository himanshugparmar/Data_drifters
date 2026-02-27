# 🚀 Quick Start Guide - Documentation Sync Pipeline

## Installation (One-Time Setup)

```bash
# 1. Install dependencies
pip install -r doc_sync_requirements.txt

# 2. Set OpenAI API key
export OPENAI_API_KEY="your-api-key-here"
```

## Usage Options

### Option 1: Quick Synchronization (Recommended)

```bash
# Synchronize current directory
python doc_sync_pipeline.py .
```

### Option 2: Programmatic Usage

```python
from doc_sync_pipeline import synchronize_documentation

result = synchronize_documentation(
    repository_path=".",
    renamed_methods=[
        {
            "class_name": "ST3215",
            "old_name": "OldMethod",
            "new_name": "NewMethod",
            "method_type": "class_method"
        }
    ]
)

print(f"Status: {result['documentation_sync_status']}")
```

### Option 3: Run Examples

```bash
# Check prerequisites
python example_sync_usage.py

# Run specific example
python example_sync_usage.py 1  # Basic sync
python example_sync_usage.py 2  # Multiple renames
python example_sync_usage.py 3  # Advanced usage
```

## Complete Workflow for Method Rename

### Scenario: Renaming `PingServo` → `LinkServo`

**Step 1: Update Python source code**
```python
# In st3215.py
class ST3215:
    def LinkServo(self, sts_id):  # Renamed from PingServo
        """Link to servo and verify connection"""
        # ... implementation ...
```

**Step 2: Run documentation sync**
```bash
python example_sync_usage.py 1
```

**Step 3: Verify results**
```bash
# Check that all changes were applied
grep -r "PingServo" *.md  # Should return nothing
grep -r "LinkServo" *.md  # Should show all updated references
```

## What Gets Synchronized

✅ Method names in code blocks  
✅ Function calls in examples  
✅ Headings and section titles  
✅ Table entries  
✅ Inline code references  
✅ Standalone mentions  

## Output Example

```
================================================================================
DOCUMENTATION SYNCHRONIZATION PIPELINE REPORT
================================================================================
Status: COMPLETE
Total Iterations: 2
Files Scanned: 6
Files Modified: 6
Total Replacements: 24
Stale References Remaining: 0
Sync Score: 100.00%
================================================================================

Modified Files:
  ✅ README.md
  ✅ User_manual.md
  ✅ user_guide.md
  ✅ troubleshooting.md
  ✅ FAQ.md
  ✅ test/README.md
```

## Troubleshooting

| Issue | Solution |
|-------|----------|
| `ModuleNotFoundError: langchain` | `pip install -r doc_sync_requirements.txt` |
| `OpenAI API key not found` | `export OPENAI_API_KEY="sk-..."` |
| Pipeline not converging | Increase `max_iterations` parameter |
| Too slow | Reduce number of files or use more specific patterns |

## File Structure

```
/home/himanshu/Data_drifters/
├── doc_sync_pipeline.py          # Main pipeline implementation
├── doc_sync_requirements.txt     # Dependencies
├── example_sync_usage.py         # Usage examples
├── DOC_SYNC_README.md            # Full documentation
└── QUICKSTART.md                 # This file
```

## Next Steps

1. ✅ Set up OpenAI API key
2. ✅ Install dependencies
3. ✅ Run example to test
4. ✅ Integrate into your workflow

## Questions?

- **Full Documentation:** See [DOC_SYNC_README.md](DOC_SYNC_README.md)
- **API Reference:** See inline docstrings in `doc_sync_pipeline.py`
- **Examples:** See `example_sync_usage.py`

---

**Time to Synchronize:** ~2-5 minutes for 6 markdown files  
**Prerequisites:** Python 3.10+, OpenAI API key  
**License:** Apache 2.0
