#!/usr/bin/env python3
"""
Diagnostic: Show all HTML files in a directory
"""

import sys
from pathlib import Path

def scan_directory(base_path):
    """Show all HTML files found."""
    
    base_path = Path(base_path)
    
    if not base_path.exists():
        print(f"❌ Error: {base_path} does not exist")
        return
    
    # Find all HTML files
    html_files = list(base_path.rglob('*.html'))
    
    if not html_files:
        print(f"❌ No HTML files found in {base_path}")
        return
    
    print(f"\n📁 Found {len(html_files)} HTML files in {base_path}")
    print("=" * 70)
    
    # Separate by type (check both Unix and Windows path separators)
    spanish_files = [f for f in html_files if '/es/' in str(f) or '\\es\\' in str(f)]
    other_files = [f for f in html_files if f not in spanish_files]
    
    if spanish_files:
        print(f"\n🇪🇸 SPANISH FILES ({len(spanish_files)}):")
        for f in spanish_files[:20]:  # Show first 20
            print(f"  ✓ {f}")
        if len(spanish_files) > 20:
            print(f"  ... and {len(spanish_files) - 20} more")
    else:
        print("\n🇪🇸 SPANISH FILES: None found")
        print("   (Looking for files with '/es/' or '\\es\\' in path)")
    
    if other_files:
        print(f"\n📄 OTHER FILES ({len(other_files)}):")
        for f in other_files[:20]:  # Show first 20
            print(f"  • {f}")
        if len(other_files) > 20:
            print(f"  ... and {len(other_files) - 20} more")
    
    print("\n" + "=" * 70)
    print("\nDone!")


def main():
    if len(sys.argv) < 2:
        print("\nUsage: python scan_files.py <directory>")
        print("\nExample: python scan_files.py districts")
        sys.exit(1)
    
    base_path = sys.argv[1]
    scan_directory(base_path)


if __name__ == '__main__':
    main()