#!/usr/bin/env python3
"""
Batch convert all ACTIVITY, LAB, HOMEWORK, and TOOL markdown files to HTML.

This script finds all assignment markdown files in the repository and converts them
to HTML using convert_activity_to_html.py
"""

import subprocess
import sys
from pathlib import Path


def find_assignment_files(repo_root: Path) -> list[Path]:
    """Find all ACTIVITY_*, LAB_*, HOMEWORK*.md, and TOOL*.md files in the repository.
    
    Searches recursively in numbered module directories (00_*, 01_*, etc.) and all their
    subdirectories (including digitalocean, positcloudconnect, positconnect, etc.).
    """
    assignment_files = []
    seen_files = set()  # Track files to avoid duplicates
    
    # Search in numbered module directories (00_*, 01_*, etc.)
    for module_dir in sorted(repo_root.glob('[0-9][0-9]_*')):
        if module_dir.is_dir():
            # Search for all assignment types in module directory and all subdirectories recursively
            # rglob searches recursively, so it will find files in subfolders like:
            # - digitalocean/
            # - positcloudconnect/
            # - positconnect/
            # - and any other subdirectories
            for pattern in ['ACTIVITY_*.md', 'LAB_*.md', 'HOMEWORK*.md', 'TOOL*.md']:
                # Use rglob to recursively search all subdirectories
                for md_file in module_dir.rglob(pattern):
                    # Resolve to absolute path and add to set to avoid duplicates
                    abs_path = md_file.resolve()
                    if abs_path not in seen_files:
                        seen_files.add(abs_path)
                        assignment_files.append(md_file)
    
    return sorted(assignment_files)


def main():
    """Main entry point."""
    # Find repo root
    repo_root = None
    current = Path(__file__).resolve().parent.parent.parent.parent
    while current != current.parent:
        if (current / '.git').exists() or (current / '.gitignore').exists():
            repo_root = current
            break
        current = current.parent
    
    if not repo_root:
        repo_root = Path.cwd()
    
    # Get the convert script path
    convert_script = Path(__file__).parent / 'convert_activity_to_html.py'
    
    if not convert_script.exists():
        print(f"Error: convert_activity_to_html.py not found at {convert_script}")
        sys.exit(1)
    
    # Find all assignment files
    assignment_files = find_assignment_files(repo_root)
    
    if not assignment_files:
        print("No ACTIVITY_*, LAB_*, HOMEWORK*.md, or TOOL*.md files found.")
        sys.exit(0)
    
    print(f"Found {len(assignment_files)} assignment file(s) to convert:\n")
    
    # Convert each file
    success_count = 0
    error_count = 0
    
    for md_file in assignment_files:
        rel_path = md_file.relative_to(repo_root)
        print(f"Converting: {rel_path}")
        
        try:
            result = subprocess.run(
                [sys.executable, str(convert_script), str(md_file)],
                capture_output=True,
                text=True,
                cwd=repo_root
            )
            
            if result.returncode == 0:
                print(f"  [OK] Success")
                success_count += 1
            else:
                print(f"  [ERROR] {result.stderr.strip()}")
                error_count += 1
        except Exception as e:
            print(f"  [EXCEPTION] {e}")
            error_count += 1
    
    print(f"\n{'='*60}")
    print(f"Summary: {success_count} succeeded, {error_count} failed")
    print(f"{'='*60}")


if __name__ == '__main__':
    main()
