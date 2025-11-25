#!/usr/bin/env python3
"""
Version Bump Script for Miolingo App

Usage:
    bump_app.py major          # Bump major version (1.2.3 -> 2.0.0)
    bump_app.py minor          # Bump minor version (1.2.3 -> 1.3.0)
    bump_app.py patch          # Bump patch version (1.2.3 -> 1.2.4)
    bump_app.py major tag      # Bump major + commit + tag
    bump_app.py minor tag      # Bump minor + commit + tag
    bump_app.py patch tag      # Bump patch + commit + tag
    bump_app.py patch tag push # Bump patch + commit + tag + push

Note: Activate virtual environment first: source venv/bin/activate
"""

import re
import sys
import subprocess
from pathlib import Path
from typing import List, Tuple
from datetime import datetime

# Configuration files
PROGRAM_FILES_LIST = "bump_program_files.txt"
DOC_FILES_LIST = "bump_doc_files.txt"

def read_file_list(filename: str) -> List[str]:
    """Read list of files from config file, ignoring comments and blank lines."""
    config_file = Path(filename)
    if not config_file.exists():
        print(f"Warning: {filename} not found, skipping")
        return []
    
    files = []
    for line in config_file.read_text().splitlines():
        line = line.strip()
        if line and not line.startswith('#'):
            files.append(line)
    return files

def find_version_in_file(filepath: str) -> Tuple[str, str]:
    """
    Find current version in file. Returns (version, pattern_type).
    Handles multiple version formats:
    - __version__ = "1.2.3"
    - **Version 1.2.3**
    - Current Version: 1.2.3
    """
    content = Path(filepath).read_text()
    
    # Pattern 1: Python __version__ = "1.2.3"
    match = re.search(r'__version__\s*=\s*["\'](\d+\.\d+\.\d+)["\']', content)
    if match:
        return match.group(1), 'python'
    
    # Pattern 2: **Version 1.2.3**
    match = re.search(r'\*\*Version\s+(\d+\.\d+\.\d+)\*\*', content)
    if match:
        return match.group(1), 'markdown_bold'
    
    # Pattern 3: Current Version: 1.2.3
    match = re.search(r'Current Version:\*\*\s+(\d+\.\d+\.\d+)', content)
    if match:
        return match.group(1), 'current_version'
    
    # Pattern 4: ## [1.2.3] - 2025-11-24 (changelog)
    match = re.search(r'##\s+\[(\d+\.\d+\.\d+)\]', content)
    if match:
        return match.group(1), 'changelog'
    
    return None, None

def bump_version(version: str, bump_type: str) -> str:
    """Increment version number based on bump type."""
    major, minor, patch = map(int, version.split('.'))
    
    if bump_type == 'major':
        return f"{major + 1}.0.0"
    elif bump_type == 'minor':
        return f"{major}.{minor + 1}.0"
    elif bump_type == 'patch':
        return f"{major}.{minor}.{patch + 1}"
    else:
        raise ValueError(f"Invalid bump type: {bump_type}")

def update_version_in_file(filepath: str, old_version: str, new_version: str, pattern_type: str) -> bool:
    """Update version in file based on pattern type."""
    path = Path(filepath)
    if not path.exists():
        print(f"  ⚠️  File not found: {filepath}")
        return False
    
    content = path.read_text()
    original_content = content
    
    if pattern_type == 'python':
        content = re.sub(
            r'(__version__\s*=\s*["\'])' + re.escape(old_version) + r'(["\'])',
            r'\g<1>' + new_version + r'\g<2>',
            content
        )
    elif pattern_type == 'markdown_bold':
        content = re.sub(
            r'(\*\*Version\s+)' + re.escape(old_version) + r'(\*\*)',
            r'\g<1>' + new_version + r'\g<2>',
            content
        )
    elif pattern_type == 'current_version':
        content = re.sub(
            r'(Current Version:\*\*\s+)' + re.escape(old_version),
            r'\g<1>' + new_version,
            content
        )
    elif pattern_type == 'changelog':
        # For changelog, add new entry at top but keep old version
        today = datetime.now().strftime('%Y-%m-%d')
        changelog_entry = f"## [{new_version}] - {today}\n\n### Changed\n\n- Version bump\n\n\n"
        # Insert after the header (usually after line starting with "##")
        lines = content.split('\n')
        insert_pos = 0
        for i, line in enumerate(lines):
            if line.startswith('## ['):
                insert_pos = i
                break
        lines.insert(insert_pos, changelog_entry)
        content = '\n'.join(lines)
    
    if content != original_content:
        path.write_text(content)
        return True
    return False

def get_current_version(files: List[str]) -> str:
    """Get current version from first file that has it."""
    for filepath in files:
        version, _ = find_version_in_file(filepath)
        if version:
            return version
    return None

def update_all_files(program_files: List[str], doc_files: List[str], bump_type: str) -> Tuple[str, str]:
    """Update version in all files. Returns (old_version, new_version)."""
    all_files = program_files + doc_files
    
    # Get current version
    current_version = get_current_version(all_files)
    if not current_version:
        print("❌ Could not find current version in any file")
        sys.exit(1)
    
    new_version = bump_version(current_version, bump_type)
    
    print(f"📦 Bumping version: {current_version} → {new_version}")
    print()
    
    updated_files = []
    
    # Update program files
    print("🔧 Program files:")
    for filepath in program_files:
        version, pattern_type = find_version_in_file(filepath)
        if version:
            if update_version_in_file(filepath, current_version, new_version, pattern_type):
                print(f"  ✅ {filepath}")
                updated_files.append(filepath)
            else:
                print(f"  ⚠️  No changes: {filepath}")
        else:
            print(f"  ⚠️  No version found: {filepath}")
    
    # Update doc files
    print("\n📚 Documentation files:")
    for filepath in doc_files:
        version, pattern_type = find_version_in_file(filepath)
        if version:
            if update_version_in_file(filepath, current_version, new_version, pattern_type):
                print(f"  ✅ {filepath}")
                updated_files.append(filepath)
            else:
                print(f"  ⚠️  No changes: {filepath}")
        else:
            print(f"  ⚠️  No version found: {filepath}")
    
    return current_version, new_version, updated_files

def git_commit_and_tag(version: str, files: List[str]):
    """Commit changes and create git tag."""
    print(f"\n📝 Committing changes...")
    
    # Add files
    subprocess.run(['git', 'add'] + files, check=True)
    
    # Commit
    commit_msg = f"v{version}: Version bump"
    subprocess.run(['git', 'commit', '-m', commit_msg], check=True)
    
    # Tag
    print(f"🏷️  Creating tag v{version}...")
    tag_msg = f"Version {version}"
    subprocess.run(['git', 'tag', '-a', f'v{version}', '-m', tag_msg], check=True)
    
    print(f"✅ Committed and tagged as v{version}")

def git_push():
    """Push commits and tags to remote."""
    print(f"\n🚀 Pushing to remote...")
    subprocess.run(['git', 'push'], check=True)
    subprocess.run(['git', 'push', '--tags'], check=True)
    print("✅ Pushed to remote")

def main():
    if len(sys.argv) < 2:
        print(__doc__)
        sys.exit(1)
    
    bump_type = sys.argv[1].lower()
    if bump_type not in ['major', 'minor', 'patch']:
        print(f"❌ Invalid bump type: {bump_type}")
        print("   Use: major, minor, or patch")
        sys.exit(1)
    
    do_tag = 'tag' in sys.argv
    do_push = 'push' in sys.argv
    
    # Read file lists
    program_files = read_file_list(PROGRAM_FILES_LIST)
    doc_files = read_file_list(DOC_FILES_LIST)
    
    if not program_files and not doc_files:
        print("❌ No files to update. Create bump_program_files.txt and/or bump_doc_files.txt")
        sys.exit(1)
    
    # Update versions
    old_version, new_version, updated_files = update_all_files(program_files, doc_files, bump_type)
    
    if not updated_files:
        print("\n⚠️  No files were updated")
        sys.exit(1)
    
    print(f"\n✅ Updated {len(updated_files)} file(s)")
    
    # Commit and tag if requested
    if do_tag:
        git_commit_and_tag(new_version, updated_files)
        
        # Push if requested
        if do_push:
            git_push()
    else:
        print("\n💡 Run with 'tag' to commit and tag: bump_app.py", bump_type, "tag")
        print("💡 Run with 'tag push' to also push: bump_app.py", bump_type, "tag push")

if __name__ == '__main__':
    main()
