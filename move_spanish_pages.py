#!/usr/bin/env python3
"""
Move Spanish pages from /es-districts/{district}/ to /districts/{district}/es/
"""

import os
import sys
import shutil
from pathlib import Path

def move_spanish_pages(es_districts_path, districts_path, delete_old=False):
    """
    Move Spanish pages to nested structure.
    
    Args:
        es_districts_path: Path to es-districts folder
        districts_path: Path to districts folder
        delete_old: If True, delete empty es-districts folders after moving
    """
    
    es_districts_path = Path(es_districts_path)
    districts_path = Path(districts_path)
    
    # Validate paths
    if not es_districts_path.exists():
        print(f"❌ Error: {es_districts_path} does not exist")
        return
    
    if not districts_path.exists():
        print(f"❌ Error: {districts_path} does not exist")
        return
    
    # Get all district folders in es-districts
    district_folders = [f for f in es_districts_path.iterdir() if f.is_dir()]
    
    if not district_folders:
        print(f"❌ No district folders found in {es_districts_path}")
        return
    
    print(f"Found {len(district_folders)} districts to move")
    print("=" * 70)
    
    total_files_moved = 0
    total_districts_processed = 0
    errors = []
    
    for district_folder in district_folders:
        district_name = district_folder.name
        
        # Target path: districts/{district}/es/
        target_base = districts_path / district_name
        target_es = target_base / 'es'
        
        # Check if English district folder exists
        if not target_base.exists():
            print(f"⚠ {district_name}: English folder doesn't exist, skipping")
            errors.append(f"{district_name}: No matching English folder")
            continue
        
        # Get all HTML files in this Spanish district folder
        html_files = list(district_folder.glob('*.html'))
        
        if not html_files:
            print(f"○ {district_name}: No HTML files found")
            continue
        
        # Create /es/ subfolder if it doesn't exist
        target_es.mkdir(parents=True, exist_ok=True)
        
        # Move each file
        files_moved = 0
        for html_file in html_files:
            target_file = target_es / html_file.name
            
            try:
                # Move the file
                shutil.move(str(html_file), str(target_file))
                files_moved += 1
            except Exception as e:
                errors.append(f"{district_name}/{html_file.name}: {str(e)}")
                print(f"✗ {district_name}/{html_file.name}: Error - {str(e)}")
        
        if files_moved > 0:
            total_files_moved += files_moved
            total_districts_processed += 1
            print(f"✓ {district_name}: Moved {files_moved} files → /districts/{district_name}/districts/es-index.html")
        
        # Delete empty folder if requested
        if delete_old:
            try:
                # Check if folder is now empty
                remaining_files = list(district_folder.glob('*'))
                if not remaining_files:
                    district_folder.rmdir()
                    print(f"  ↳ Deleted empty folder: {district_name}")
            except Exception as e:
                print(f"  ⚠ Could not delete {district_name}: {str(e)}")
    
    print("=" * 70)
    print(f"\n✓ Districts processed: {total_districts_processed}")
    print(f"✓ Total files moved: {total_files_moved}")
    
    if errors:
        print(f"\n⚠ Errors encountered: {len(errors)}")
        for error in errors[:10]:  # Show first 10 errors
            print(f"  • {error}")
        if len(errors) > 10:
            print(f"  ... and {len(errors) - 10} more")
    
    print("\nDone!")


def main():
    if len(sys.argv) < 3:
        print("=" * 70)
        print("MOVE SPANISH PAGES TO NESTED STRUCTURE")
        print("=" * 70)
        print("\nUsage:")
        print("  python move_spanish_pages.py <es-districts-path> <districts-path> [--delete-old]")
        print("\nExamples:")
        print("  python move_spanish_pages.py es-districts districts")
        print("  python move_spanish_pages.py es-districts districts --delete-old")
        print("\nOptions:")
        print("  --delete-old    Delete empty es-districts folders after moving")
        print("\nBefore/After:")
        print("  OLD: /es-districts/anna-isd/ard-guide.html")
        print("  NEW: /districts/anna-isd/es/ard-guide.html")
        print("=" * 70)
        sys.exit(1)
    
    es_districts = sys.argv[1]
    districts = sys.argv[2]
    delete_old = '--delete-old' in sys.argv
    
    if delete_old:
        print("⚠ WARNING: Empty folders will be deleted after moving")
        response = input("Continue? (y/n): ")
        if response.lower() != 'y':
            print("Cancelled.")
            sys.exit(0)
    
    move_spanish_pages(es_districts, districts, delete_old)


if __name__ == '__main__':
    main()