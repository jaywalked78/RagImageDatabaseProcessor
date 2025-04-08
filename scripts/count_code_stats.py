#!/usr/bin/env python
"""
Code Statistics Counting Script

This script analyzes the codebase to count:
1. Total lines of code
2. Total words
3. Total characters
4. Statistics by file extension

Usage:
  python count_code_stats.py [--exclude-patterns pattern1,pattern2]

Example:
  python count_code_stats.py --exclude-patterns "*.md,docs/*,README*"
"""

import os
import re
import sys
import argparse
from pathlib import Path
import fnmatch
import time

# Default file patterns to exclude
DEFAULT_EXCLUDE_PATTERNS = [
    "*.md",                # Markdown files
    "LICENSE*",            # License files
    "docs/*",              # Documentation directory
    "*.json",              # JSON files
    "*.log",               # Log files
    ".git/*",              # Git directory
    ".github/*",           # GitHub directory
    "__pycache__/*",       # Python cache
    "*.pyc",               # Python compiled files
    "*.pyo",               # Python optimized files
    "*.pyd",               # Python dynamic modules
    "*.so",                # Shared object files
    "*.o",                 # Object files
    "*.a",                 # Static library files
    "*.lib",               # Library files
    "*.dll",               # Dynamic link libraries
    "*.exe",               # Executable files
    "*.bin",               # Binary files
    "*.obj",               # Object files
    "*.jpg",               # Image files
    "*.jpeg",              # Image files
    "*.png",               # Image files
    "*.gif",               # Image files
    "*.ico",               # Icon files
    "*.svg",               # SVG files
    "*.pdf",               # PDF files
    "*.zip",               # Zip archives
    "*.gz",                # Gzip archives
    "*.tar",               # Tar archives
    "*.env*",              # Environment files
    "venv/*",              # Virtual environment
    "node_modules/*",      # Node modules
    "dist/*",              # Distribution directory
    "build/*",             # Build directory
    "coverage/*",          # Coverage reports
]

def should_exclude(file_path, exclude_patterns):
    """Check if a file should be excluded based on patterns."""
    for pattern in exclude_patterns:
        if fnmatch.fnmatch(file_path, pattern):
            return True
    return False

def count_file_stats(file_path):
    """Count statistics for a single file."""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='replace') as f:
            content = f.read()
            
            # Count statistics
            lines = content.count('\n') + (1 if content and content[-1] != '\n' else 0)
            words = len(re.findall(r'\b\w+\b', content))
            chars = len(content)
            
            return {
                'lines': lines,
                'words': words,
                'chars': chars,
                'size': os.path.getsize(file_path)
            }
    except Exception as e:
        print(f"Error processing {file_path}: {e}")
        return {
            'lines': 0,
            'words': 0,
            'chars': 0,
            'size': 0
        }

def get_file_extension(file_path):
    """Get the file extension or type for categorization."""
    ext = os.path.splitext(file_path)[1].lower()
    
    if not ext:
        # For files without extension, use the name (e.g., Makefile, Dockerfile)
        return os.path.basename(file_path)
    
    return ext

def scan_directory(start_path, exclude_patterns):
    """Scan directory recursively and count stats."""
    total_stats = {
        'files': 0,
        'lines': 0,
        'words': 0,
        'chars': 0,
        'size': 0,
        'extensions': {}
    }
    
    excluded_files = 0
    
    for root, dirs, files in os.walk(start_path):
        # Filter out excluded directories
        dirs[:] = [d for d in dirs if not should_exclude(os.path.join(root, d), exclude_patterns)]
        
        for file in files:
            file_path = os.path.join(root, file)
            rel_path = os.path.relpath(file_path, start_path)
            
            if should_exclude(rel_path, exclude_patterns):
                excluded_files += 1
                continue
            
            # Count stats for this file
            stats = count_file_stats(file_path)
            ext = get_file_extension(file_path)
            
            # Update total stats
            total_stats['files'] += 1
            total_stats['lines'] += stats['lines']
            total_stats['words'] += stats['words']
            total_stats['chars'] += stats['chars']
            total_stats['size'] += stats['size']
            
            # Update extension stats
            if ext not in total_stats['extensions']:
                total_stats['extensions'][ext] = {
                    'files': 0,
                    'lines': 0,
                    'words': 0,
                    'chars': 0,
                    'size': 0
                }
            
            total_stats['extensions'][ext]['files'] += 1
            total_stats['extensions'][ext]['lines'] += stats['lines']
            total_stats['extensions'][ext]['words'] += stats['words']
            total_stats['extensions'][ext]['chars'] += stats['chars']
            total_stats['extensions'][ext]['size'] += stats['size']
    
    return total_stats, excluded_files

def format_size(size_bytes):
    """Format size in bytes to human-readable format."""
    for unit in ['B', 'KB', 'MB', 'GB']:
        if size_bytes < 1024 or unit == 'GB':
            return f"{size_bytes:.2f} {unit}"
        size_bytes /= 1024

def display_results(stats, excluded_files, start_time):
    """Display the results in a formatted way."""
    duration = time.time() - start_time
    
    print("\n=========================================")
    print("           CODE STATISTICS              ")
    print("=========================================")
    print(f"Total files analyzed: {stats['files']}")
    print(f"Files excluded: {excluded_files}")
    print(f"Analysis time: {duration:.2f} seconds")
    print("-----------------------------------------")
    print(f"Total lines of code: {stats['lines']:,}")
    print(f"Total words: {stats['words']:,}")
    print(f"Total characters: {stats['chars']:,}")
    print(f"Total size: {format_size(stats['size'])}")
    print("-----------------------------------------")
    
    # Sort extensions by lines of code
    sorted_extensions = sorted(
        stats['extensions'].items(),
        key=lambda x: x[1]['lines'],
        reverse=True
    )
    
    print("\nStatistics by file type:")
    print("-----------------------------------------")
    print(f"{'Extension':<10} {'Files':<10} {'Lines':<12} {'Words':<12} {'Size':<10}")
    print("-----------------------------------------")
    
    for ext, ext_stats in sorted_extensions:
        print(f"{ext:<10} {ext_stats['files']:<10} {ext_stats['lines']:<12} "
              f"{ext_stats['words']:<12} {format_size(ext_stats['size']):<10}")
    
    print("=========================================")

def main():
    parser = argparse.ArgumentParser(description='Count statistics in codebase')
    parser.add_argument('--exclude-patterns', type=str, default=','.join(DEFAULT_EXCLUDE_PATTERNS),
                        help='Comma-separated list of file patterns to exclude')
    parser.add_argument('--path', type=str, default='.',
                        help='Path to the codebase to analyze')
    
    args = parser.parse_args()
    
    exclude_patterns = args.exclude_patterns.split(',')
    start_path = os.path.abspath(args.path)
    
    print(f"Analyzing codebase in: {start_path}")
    print(f"Excluding patterns: {exclude_patterns}")
    
    start_time = time.time()
    stats, excluded_files = scan_directory(start_path, exclude_patterns)
    display_results(stats, excluded_files, start_time)

if __name__ == "__main__":
    main() 