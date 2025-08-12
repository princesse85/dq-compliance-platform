#!/usr/bin/env python3
"""
Script to replace print statements with proper logging throughout the codebase.
This ensures consistent logging and removes development artifacts.
"""

import os
import re
from pathlib import Path

def add_logging_import(file_path):
    """Add logging import to a Python file if not already present."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Check if logging import already exists
    if 'from src.utils.logging_config import get_logger' in content:
        return content
    
    # Find the last import statement
    lines = content.split('\n')
    import_end = 0
    
    for i, line in enumerate(lines):
        if line.strip().startswith(('import ', 'from ')):
            import_end = i + 1
    
    # Add logging import after other imports
    lines.insert(import_end, 'from src.utils.logging_config import get_logger')
    lines.insert(import_end + 1, '')
    lines.insert(import_end + 2, 'logger = get_logger(__name__)')
    
    return '\n'.join(lines)

def replace_print_statements(file_path):
    """Replace print statements with logger calls."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Add logging import if needed
    content = add_logging_import(file_path)
    
    # Replace print statements with logger.info
    # Handle different print statement patterns
    patterns = [
        (r'print\(f?"([^"]*)"\)', r'logger.info(r"\1")'),
        (r'print\(f?"([^"]*)"\)', r'logger.info(r"\1")'),
        (r'print\(([^)]+)\)', r'logger.info(\1)'),
        (r'print\(\)', r'logger.info("")'),
    ]
    
    for pattern, replacement in patterns:
        content = re.sub(pattern, replacement, content)
    
    return content

def cleanup_file(file_path):
    """Clean up a single Python file."""
    print(f"Cleaning {file_path}")
    
    try:
        new_content = replace_print_statements(file_path)
        
        with open(file_path, 'w', encoding='utf-8') as f:
            f.write(new_content)
        
        print(f"✅ Cleaned {file_path}")
        
    except Exception as e:
        print(f"❌ Error cleaning {file_path}: {e}")

def main():
    """Main cleanup function."""
    # Get all Python files in src directory
    src_dir = Path("src")
    python_files = list(src_dir.rglob("*.py"))
    
    print(f"Found {len(python_files)} Python files to clean")
    
    for file_path in python_files:
        cleanup_file(file_path)
    
    print("✅ Print statement cleanup completed!")

if __name__ == "__main__":
    main()
