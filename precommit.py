"""
Pre-commit hook: Auto-update version and RELEASE-NOTES in kbe.py
"""

import re
import sys
import os
from pathlib import Path
from subprocess import run, PIPE

PYTHON_FILE = "kbe.py"

def get_commit_message():
    """Extract commit message from git."""
    result = run(['git', 'log', '--format=%B', '-n', '1'], capture_output=True, text=True)
    return result.stdout.strip() if result.returncode == 0 else ""

def parse_version(version_str):
    """Parse semantic version string."""
    parts = version_str.split('.')
    return int(parts[0]), int(parts[1]), int(parts[2])

def format_version(major, minor, patch):
    """Format version tuple to string."""
    return f"{major}.{minor}.{patch}"

def get_current_version(file_path):
    """Extract version from kbe.py."""
    with open(file_path, 'r', encoding='utf-8') as f:
        match = re.search(r'Version:\s+(\d+\.\d+\.\d+)', f.read())
    return match.group(1) if match else None

def bump_version(version_str, commit_msg):
    """Determine new version based on commit message."""
    major, minor, patch = parse_version(version_str)
    
    if 'major' in commit_msg.lower():
        return format_version(major + 1, 0, 0)
    elif 'minor' in commit_msg.lower():
        return format_version(major, minor + 1, 0)
    else:
        return format_version(major, minor, patch + 1)

def update_version(file_path, old_version, new_version):
    """Update version string in file."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    content = re.sub(
        rf'Version:\s+{re.escape(old_version)}',
        f'Version:        {new_version}',
        content
    )
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(content)

def update_release_notes(file_path, release_note, new_version):
    """Insert new entry into RELEASE-NOTES section."""
    with open(file_path, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # Find RELEASE-NOTES section and insert after the colon
    pattern = r'(RELEASE-NOTES:)(.*?)(=+)'
    replacement = rf'\1\n    • {release_note} (v{new_version})\2\3'
    
    updated = re.sub(pattern, replacement, content, flags=re.DOTALL)
    
    with open(file_path, 'w', encoding='utf-8') as f:
        f.write(updated)

def main():
    """Main hook logic."""
    if not os.path.exists(PYTHON_FILE):
        sys.exit(0)
    
    # Get commit message
    commit_msg = get_commit_message()
    if not commit_msg:
        sys.exit(0)
    
    # Get current version
    current_version = get_current_version(PYTHON_FILE)
    if not current_version:
        print("Error: Could not find version in kbe.py", file=sys.stderr)
        sys.exit(1)
    
    # Calculate new version
    new_version = bump_version(current_version, commit_msg)
    
    # Only proceed if version changed
    if current_version == new_version:
        sys.exit(0)
    
    # Update files
    try:
        update_version(PYTHON_FILE, current_version, new_version)
        release_note = commit_msg.split('\n')[0]  # First line of commit message
        update_release_notes(PYTHON_FILE, release_note, new_version)
        
        # Stage the updated file
        run(['git', 'add', PYTHON_FILE], check=True)
        
        print(f"✓ Updated {PYTHON_FILE}: v{current_version} → v{new_version}")
        print(f"  Release note: {release_note}")
    except Exception as e:
        print(f"Error: {e}", file=sys.stderr)
        sys.exit(1)

if __name__ == '__main__':
    main()