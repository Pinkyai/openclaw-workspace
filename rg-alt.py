#!/usr/bin/env python3
"""
ripgrep alternative for text searching - Sebastian's Task Hub
Usage: python3 rg-alt.py pattern [directory] [options]
"""

import os
import re
import sys
import argparse
from pathlib import Path

def search_file(file_path, pattern, regex=False, case_insensitive=False, line_numbers=True):
    """Search for pattern in a single file"""
    try:
        with open(file_path, 'r', encoding='utf-8', errors='ignore') as f:
            for line_num, line in enumerate(f, 1):
                line = line.rstrip('\n\r')
                
                if regex:
                    flags = re.IGNORECASE if case_insensitive else 0
                    if re.search(pattern, line, flags):
                        yield (line_num, line) if line_numbers else (None, line)
                else:
                    search_line = line.lower() if case_insensitive else line
                    search_pattern = pattern.lower() if case_insensitive else pattern
                    if search_pattern in search_line:
                        yield (line_num, line) if line_numbers else (None, line)
    except (IOError, UnicodeDecodeError):
        pass

def search_directory(directory, pattern, regex=False, case_insensitive=False, 
                    line_numbers=True, file_names=True, recursive=True, 
                    include_hidden=False, max_depth=None):
    """Search for pattern in directory"""
    directory = Path(directory)
    
    if not directory.exists():
        print(f"Directory not found: {directory}", file=sys.stderr)
        return
    
    if recursive:
        pattern_iter = directory.rglob('*') if max_depth is None else directory.glob('**/*')
    else:
        pattern_iter = directory.iterdir()
    
    for item in pattern_iter:
        if item.is_file():
            # Skip hidden files unless requested
            if not include_hidden and item.name.startswith('.'):
                continue
            
            # Skip binary files (simple check)
            if item.suffix.lower() in ['.png', '.jpg', '.jpeg', '.gif', '.pdf', '.zip', '.tar', '.gz']:
                continue
            
            matches = list(search_file(item, pattern, regex, case_insensitive, line_numbers))
            if matches:
                if file_names:
                    print(f"\n{item}:")
                
                for line_num, line in matches:
                    if line_numbers and line_num:
                        print(f"{line_num}:{line}")
                    else:
                        print(line)

def main():
    parser = argparse.ArgumentParser(description='Simple ripgrep alternative')
    parser.add_argument('pattern', help='Search pattern')
    parser.add_argument('path', nargs='?', default='.', help='File or directory to search (default: current directory)')
    parser.add_argument('-i', '--ignore-case', action='store_true', help='Case insensitive search')
    parser.add_argument('-r', '--regex', action='store_true', help='Use regex pattern')
    parser.add_argument('-n', '--no-line-numbers', action='store_true', help='Hide line numbers')
    parser.add_argument('-H', '--no-filename', action='store_true', help='Hide filenames')
    parser.add_argument('--no-recursive', action='store_true', help='Don\'t search recursively')
    parser.add_argument('--hidden', action='store_true', help='Include hidden files')
    parser.add_argument('--max-depth', type=int, help='Maximum search depth')
    
    args = parser.parse_args()
    
    path = Path(args.path)
    
    if path.is_file():
        # Single file search
        matches = list(search_file(path, args.pattern, args.regex, args.ignore_case, not args.no_line_numbers))
        if matches:
            for line_num, line in matches:
                if not args.no_line_numbers and line_num:
                    print(f"{line_num}:{line}")
                else:
                    print(line)
    else:
        # Directory search
        search_directory(
            path, 
            args.pattern, 
            regex=args.regex,
            case_insensitive=args.ignore_case,
            line_numbers=not args.no_line_numbers,
            file_names=not args.no_filename,
            recursive=not args.no_recursive,
            include_hidden=args.hidden,
            max_depth=args.max_depth
        )

if __name__ == '__main__':
    main()