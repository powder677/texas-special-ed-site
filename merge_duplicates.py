#!/usr/bin/env python3
"""
Merge duplicate district folders (uppercase into lowercase)
If both ANNA-ISD and anna-isd exist, merge files into anna-isd and delete ANNA-ISD
"""

import sys
import shutil
from pathlib import Path

def merge_duplicates(base_path, delete_uppercase=False):
    """
    Merge uppercase folders into lowercase versions.
    
    Args:
        base_path: Directory containing district folders
        delete_uppercase: If True, delete uppercase folders after merging
    """
    
    base_path = Path(base_path)
    
    if not base_path.exists():
        print(f"❌ Error: {base_path} does not exist")
        return
    
    folders = [f for f in base_path.iterdir() if f.is_dir()]
    
    # Group folders by lowercase name
    lowercase_map = {}
    for folder in folders:
        lowercase_name = folder.name.lower()
        if lowercase_name not in lowercase_map:
            lowercase_map[lowercase_name] = []
        lowercase_map[lowercase_name].append(folder)
    
    # Find duplicates
    duplicates = {k: v for k, v in lowercase_map.items() if len(v) > 1}
    
    if not duplicates:
        print("✓ No duplicates found - nothing to merge")
        return
    
    print(f"Found {len(duplicates)} districts with duplicates")
    print("=" * 70)
    
    total_merged = 0
    total_files_moved = 0
    
    for lowercase_name, folder_list in sorted(duplicates.items()):
        # Find the lowercase folder (target) and uppercase folders (sources)
        target = None
        sources = []
        
        for folder in folder_list:
            if folder.name == lowercase_name:
                target = folder
            else:
                sources.append(folder)
        
        # If lowercase doesn't exist, rename the first uppercase one
        if target is None:
            target = base_path / lowercase_name
            first_source = sources.pop(0)
            print(f"○ {first_source.name} → {lowercase_name} (renaming)")
            first_source.rename(target)
        
        # Merge files from uppercase folders into lowercase
        for source in sources:
            html_files = list(source.glob('*.html'))
            
            if not html_files:
                print(f"○ {source.name}: No files to merge")
                continue
            
            files_moved = 0
            conflicts = 0
            
            for html_file in html_files:
                target_file = target / html_file.name
                
                # Check if file already exists in target
                if target_file.exists():
                    conflicts += 1
                    print(f"  ⚠ {html_file.name}: Already exists in {lowercase_name}, skipping")
                else:
                    shutil.move(str(html_file), str(target_file))
                    files_moved += 1
            
            total_files_moved += files_moved
            
            if files_moved > 0 or conflicts > 0:
                print(f"✓ {source.name} → {lowercase_name}: Moved {files_moved} files" + 
                      (f", {conflicts} conflicts" if conflicts > 0 else ""))
            
            # Delete uppercase folder if requested and it's empty
            if delete_uppercase:
                remaining_files = list(source.glob('*'))
                if not remaining_files:
                    source.rmdir()
                    print(f"  ↳ Deleted empty folder: {source.name}")
                    total_merged += 1
                else:
                    print(f"  ⚠ {source.name} still has {len(remaining_files)} files, not deleting")
    
    print("=" * 70)
    print(f"\n✓ Total files moved: {total_files_moved}")
    if delete_uppercase:
        print(f"✓ Uppercase folders deleted: {total_merged}")
    print("\nDone!")


def main():
    if len(sys.argv) < 2:
        print("=" * 70)
        print("MERGE DUPLICATE DISTRICT FOLDERS")
        print("=" * 70)
        print("\nUsage:")
        print("  python merge_duplicates.py <directory> [--delete-uppercase]")
        print("\nExamples:")
        print("  python merge_duplicates.py es-districts")
        print("  python merge_duplicates.py es-districts --delete-uppercase")
        print("\nOptions:")
        print("  --delete-uppercase    Delete empty uppercase folders after merging")
        print("\nWhat it does:")
        print("  Merges files from 'ANNA-ISD' into 'anna-isd'")
        print("  Keeps lowercase version as the final folder")
        print("=" * 70)
        sys.exit(1)
    
    base_path = sys.argv[1]
    delete_uppercase = '--delete-uppercase' in sys.argv
    
    if delete_uppercase:
        print("⚠ WARNING: Empty uppercase folders will be deleted after merging")
        response = input("Continue? (y/n): ")
        if response.lower() != 'y':
            print("Cancelled.")
            sys.exit(0)
    
    merge_duplicates(base_path, delete_uppercase)


if __name__ == '__main__':
    main()