#!/usr/bin/env python3
"""
Compare es-district (singular) vs es-districts (plural) to see which to keep
"""

from pathlib import Path

def compare_folders():
    """Compare the two folders and recommend which to keep."""
    
    singular = Path('es-district')
    plural = Path('es-districts')
    
    print("=" * 70)
    print("COMPARING ES-DISTRICT FOLDERS")
    print("=" * 70)
    
    # Check if they exist
    singular_exists = singular.exists()
    plural_exists = plural.exists()
    
    if not singular_exists and not plural_exists:
        print("❌ Neither es-district nor es-districts exists")
        return
    
    if not singular_exists:
        print("○ es-district/ (singular) does NOT exist")
        print("✓ es-districts/ (plural) EXISTS")
        print("\n✓ RECOMMENDATION: Keep es-districts (it's the only one)")
        return
    
    if not plural_exists:
        print("✓ es-district/ (singular) EXISTS")
        print("○ es-districts/ (plural) does NOT exist")
        print("\n✓ RECOMMENDATION: Rename es-district to es-districts")
        return
    
    # Both exist - compare them
    print("\n⚠ BOTH FOLDERS EXIST - Analyzing...\n")
    
    # Count subfolders and files in each
    singular_districts = [f for f in singular.iterdir() if f.is_dir()]
    plural_districts = [f for f in plural.iterdir() if f.is_dir()]
    
    singular_html = list(singular.rglob('*.html'))
    plural_html = list(plural.rglob('*.html'))
    
    print(f"es-district/ (singular):")
    print(f"  • {len(singular_districts)} district folders")
    print(f"  • {len(singular_html)} total HTML files")
    
    if singular_districts:
        print(f"  • Sample districts: {', '.join([d.name for d in singular_districts[:5]])}")
    
    print(f"\nes-districts/ (plural):")
    print(f"  • {len(plural_districts)} district folders")
    print(f"  • {len(plural_html)} total HTML files")
    
    if plural_districts:
        print(f"  • Sample districts: {', '.join([d.name for d in plural_districts[:5]])}")
    
    # Recommendation
    print("\n" + "=" * 70)
    print("RECOMMENDATION:")
    print("=" * 70)
    
    if len(singular_html) == 0 and len(plural_html) > 0:
        print("✓ DELETE: es-district/ (singular) - it's empty")
        print("✓ KEEP: es-districts/ (plural) - it has content")
    elif len(plural_html) == 0 and len(singular_html) > 0:
        print("✓ RENAME: es-district/ to es-districts/")
        print("✓ DELETE: es-districts/ (plural) - it's empty")
    elif len(singular_html) > len(plural_html):
        print("✓ KEEP: es-district/ (singular) - it has more content")
        print("⚠ CHECK: es-districts/ (plural) - might be old/duplicate")
    elif len(plural_html) > len(singular_html):
        print("✓ KEEP: es-districts/ (plural) - it has more content")
        print("⚠ CHECK: es-district/ (singular) - might be old/duplicate")
    else:
        print("⚠ BOTH have similar content - manual review needed")
        print("  Compare the district names to see if they're duplicates")
    
    print("=" * 70)


if __name__ == '__main__':
    compare_folders()