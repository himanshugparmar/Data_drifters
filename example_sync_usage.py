#!/usr/bin/env python3
"""
Example Usage of LangChain Documentation Synchronization Pipeline

This script demonstrates how to use the doc_sync_pipeline.py to automatically
synchronize documentation after code changes.

Prerequisites:
    pip install -r doc_sync_requirements.txt
    export OPENAI_API_KEY="your-api-key-here"
"""

import os
import sys
from doc_sync_pipeline import (
    synchronize_documentation,
    DocumentationSyncPipeline,
    RenamedMethod
)


def example_1_basic_sync():
    """Basic synchronization for a single method rename"""
    print("=" * 80)
    print("EXAMPLE 1: Basic Method Rename Synchronization")
    print("=" * 80)
    
    result = synchronize_documentation(
        repository_path="/home/himanshu/Data_drifters",
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
    
    print(f"\nStatus: {result['documentation_sync_status']}")
    print(f"Files Modified: {result['total_files_modified']}")
    print(f"Sync Score: {result['sync_score']:.2%}")
    print(f"Iterations: {result['total_iterations']}")
    
    return result


def example_2_multiple_renames():
    """Synchronization for multiple method renames"""
    print("\n" + "=" * 80)
    print("EXAMPLE 2: Multiple Method Renames")
    print("=" * 80)
    
    result = synchronize_documentation(
        repository_path="/home/himanshu/Data_drifters",
        renamed_methods=[
            {
                "class_name": "ST3215",
                "old_name": "ReadPos",
                "new_name": "GetPosition",
                "method_type": "class_method"
            },
            {
                "class_name": "ST3215",
                "old_name": "WritePos",
                "new_name": "SetPosition",
                "method_type": "class_method"
            },
            {
                "class_name": "ST3215",
                "old_name": "ReadVoltage",
                "new_name": "GetVoltage",
                "method_type": "class_method"
            }
        ],
        max_iterations=10
    )
    
    print(f"\nStatus: {result['documentation_sync_status']}")
    print(f"Files Modified: {result['total_files_modified']}")
    print(f"Sync Score: {result['sync_score']:.2%}")
    
    return result


def example_3_advanced_usage():
    """Advanced usage with custom pipeline configuration"""
    print("\n" + "=" * 80)
    print("EXAMPLE 3: Advanced Pipeline Configuration")
    print("=" * 80)
    
    # Define method changes
    method_changes = [
        RenamedMethod(
            class_name="ST3215",
            old_name="OldMethodName",
            new_name="NewMethodName",
            method_type="class_method"
        )
    ]
    
    # Create pipeline instance
    pipeline = DocumentationSyncPipeline(
        repository_path="/home/himanshu/Data_drifters",
        method_changes=method_changes,
        max_iterations=15
    )
    
    # Execute pipeline
    result = pipeline.execute()
    
    # Access detailed reports
    print("\n--- Scan Report ---")
    scan_report = result["final_scan_report"]
    print(f"Files scanned: {len(scan_report['files_scanned'])}")
    print(f"Stale references: {scan_report['stale_references_found']}")
    print(f"Sync score: {scan_report['documentation_sync_score']:.2%}")
    
    print("\n--- Modification Report ---")
    mod_report = result["final_modification_report"]
    print(f"Files modified: {len(mod_report['files_modified'])}")
    print(f"Total replacements: {mod_report['total_replacements']}")
    print(f"Validation success: {mod_report['success']}")
    
    return result


def example_4_dry_run_scan():
    """Scan documentation without modifying files"""
    print("\n" + "=" * 80)
    print("EXAMPLE 4: Dry Run - Scan Only")
    print("=" * 80)
    
    # This would require implementing a scan_only mode in the pipeline
    # For demonstration purposes only
    
    method_changes = [
        RenamedMethod(
            class_name="ST3215",
            old_name="TestMethod",
            new_name="TestMethodNew",
            method_type="class_method"
        )
    ]
    
    pipeline = DocumentationSyncPipeline(
        repository_path="/home/himanshu/Data_drifters",
        method_changes=method_changes,
        max_iterations=1  # Run only once for scanning
    )
    
    result = pipeline.execute()
    
    print("\n--- Files Needing Changes ---")
    scan_report = result["final_scan_report"]
    for file_plan in scan_report['change_plan']:
        print(f"  {file_plan['file_path']}")
        print(f"    Priority: {file_plan['priority']}")
        print(f"    Stale refs: {file_plan['stale_references_count']}")
    
    return result


def check_prerequisites():
    """Check if all prerequisites are met"""
    print("Checking prerequisites...")
    
    # Check OpenAI API key
    if not os.getenv("OPENAI_API_KEY"):
        print("❌ OPENAI_API_KEY not found in environment")
        print("   Set it with: export OPENAI_API_KEY='your-key-here'")
        return False
    else:
        print("✅ OPENAI_API_KEY found")
    
    # Check if doc_sync_pipeline.py exists
    pipeline_path = os.path.join(os.path.dirname(__file__), "doc_sync_pipeline.py")
    if not os.path.exists(pipeline_path):
        print(f"❌ doc_sync_pipeline.py not found at {pipeline_path}")
        return False
    else:
        print("✅ doc_sync_pipeline.py found")
    
    # Check LangChain installation
    try:
        import langchain
        import langgraph
        import pydantic
        print("✅ LangChain dependencies installed")
    except ImportError as e:
        print(f"❌ Missing dependency: {e}")
        print("   Install with: pip install -r doc_sync_requirements.txt")
        return False
    
    print("\nAll prerequisites met! ✅\n")
    return True


def main():
    """Main entry point for example script"""
    
    # Check prerequisites
    if not check_prerequisites():
        print("\nPlease fix the issues above before running the pipeline.")
        sys.exit(1)
    
    # Parse command line arguments
    if len(sys.argv) > 1:
        example_name = sys.argv[1]
    else:
        print("Usage: python example_sync_usage.py [example_number]")
        print("Examples:")
        print("  1 - Basic method rename")
        print("  2 - Multiple method renames")
        print("  3 - Advanced configuration")
        print("  4 - Dry run scan")
        print("\nRunning all examples by default...\n")
        example_name = "all"
    
    # Run selected example
    try:
        if example_name == "1":
            example_1_basic_sync()
        elif example_name == "2":
            example_2_multiple_renames()
        elif example_name == "3":
            example_3_advanced_usage()
        elif example_name == "4":
            example_4_dry_run_scan()
        elif example_name == "all":
            example_1_basic_sync()
            # Uncomment to run additional examples
            # example_2_multiple_renames()
            # example_3_advanced_usage()
            # example_4_dry_run_scan()
        else:
            print(f"Unknown example: {example_name}")
            sys.exit(1)
            
    except Exception as e:
        print(f"\n❌ Error running pipeline: {e}")
        import traceback
        traceback.print_exc()
        sys.exit(1)
    
    print("\n" + "=" * 80)
    print("Example completed successfully! ✅")
    print("=" * 80)


if __name__ == "__main__":
    main()
