#!/usr/bin/env python3
"""
Lowercase all capitalized district folder names in es-districts
"""

import os
import sys
from pathlib import Path

def lowercase_folders(base_path):
    """Rename all capitalized district folders to lowercase."""
    
    base_path = Path(base_path)
    
    if not base_path.exists():
        print(f"❌ Error: {base_path} does not exist")
        return
    
    # Get all subdirectories
    folders = [f for f in base_path.iterdir() if f.is_dir()]
    
    if not folders:
        print(f"❌ No folders found in {base_path}")
        return
    
    print(f"Found {len(folders)} folders in {base_path}")
    print("=" * 70)
    
    renamed = 0
    skipped = 0
    
    for folder in folders:
        folder_name = folder.name
        lowercase_name = folder_name.lower()
        
        # Skip if already lowercase
        if folder_name == lowercase_name:
            skipped += 1
            print(f"○ {folder_name}: Already lowercase")
            continue
        
        # New path
        new_path = folder.parent / lowercase_name
        
        # Check if target already exists
        if new_path.exists():
            print(f"⚠ {folder_name}: Target '{lowercase_name}' already exists, skipping")
            skipped += 1
            continue
        
        # Rename
        try:
            folder.rename(new_path)
            renamed += 1
            print(f"✓ {folder_name} → {lowercase_name}")
        except Exception as e:
            print(f"✗ {folder_name}: Error - {str(e)}")
    
    print("=" * 70)
    print(f"\n✓ Renamed: {renamed} folders")
    print(f"○ Skipped: {skipped} folders")
    print("\nDone!")


def main():
    if len(sys.argv) < 2:
        print("=" * 70)
        print("LOWERCASE DISTRICT FOLDERS")
        print("=" * 70)
        print("\nUsage:")
        print("  python lowercase_districts.py <directory>")
        print("\nExample:")
        print("  python lowercase_districts.py es-districts")
        print("=" * 70)
        sys.exit(1)
    
    input_path = sys.argv[1]
    lowercase_folders(input_path)


if __name__ == '__main__':
    main()