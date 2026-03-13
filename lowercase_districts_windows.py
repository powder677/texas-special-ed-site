#!/usr/bin/env python3
"""
Windows-safe lowercase rename (two-step process for case-insensitive filesystems)
"""

import sys
import time
from pathlib import Path

def lowercase_folders_windows(base_path):
    """Rename folders to lowercase using two-step process for Windows."""
    
    base_path = Path(base_path)
    
    if not base_path.exists():
        print(f"❌ Error: {base_path} does not exist")
        return
    
    folders = [f for f in base_path.iterdir() if f.is_dir()]
    
    if not folders:
        print(f"❌ No folders found in {base_path}")
        return
    
    print(f"Found {len(folders)} folders in {base_path}")
    print("=" * 70)
    
    renamed = 0
    skipped = 0
    errors = 0
    
    for folder in folders:
        folder_name = folder.name
        lowercase_name = folder_name.lower()
        
        # Skip if already lowercase
        if folder_name == lowercase_name:
            skipped += 1
            # Don't print every skip - too noisy
            continue
        
        # Two-step rename for Windows:
        # Step 1: Rename to temporary name
        # Step 2: Rename to final lowercase name
        
        temp_name = f"_temp_{lowercase_name}_"
        temp_path = folder.parent / temp_name
        final_path = folder.parent / lowercase_name
        
        try:
            # Step 1: Rename to temp
            folder.rename(temp_path)
            
            # Small delay to ensure filesystem updates
            time.sleep(0.01)
            
            # Step 2: Rename temp to final lowercase
            temp_path.rename(final_path)
            
            renamed += 1
            print(f"✓ {folder_name} → {lowercase_name}")
            
        except Exception as e:
            errors += 1
            print(f"✗ {folder_name}: Error - {str(e)}")
            
            # Try to clean up temp folder if it exists
            if temp_path.exists():
                try:
                    temp_path.rename(folder)
                except:
                    pass
    
    print("=" * 70)
    print(f"\n✓ Renamed: {renamed} folders")
    print(f"○ Skipped: {skipped} folders (already lowercase)")
    if errors > 0:
        print(f"✗ Errors: {errors} folders")
    print("\nDone!")


def main():
    if len(sys.argv) < 2:
        print("=" * 70)
        print("LOWERCASE DISTRICT FOLDERS (WINDOWS-SAFE)")
        print("=" * 70)
        print("\nUsage:")
        print("  python lowercase_districts_windows.py <directory>")
        print("\nExample:")
        print("  python lowercase_districts_windows.py es-districts")
        print("\nNote:")
        print("  Uses two-step rename to work on Windows case-insensitive filesystem")
        print("=" * 70)
        sys.exit(1)
    
    input_path = sys.argv[1]
    lowercase_folders_windows(input_path)


if __name__ == '__main__':
    main()