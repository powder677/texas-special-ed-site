"""
Site File Diagnostics
======================
Run this to see exactly what HTML files exist locally and what's missing.

Usage:
    python diagnose_files.py --dir .
"""

import os
import argparse
from collections import defaultdict

def main():
    parser = argparse.ArgumentParser()
    parser.add_argument("--dir", required=True, help="Root folder of your site")
    args = parser.parse_args()

    site_dir = os.path.abspath(args.dir)
    print(f"\nScanning: {site_dir}\n")

    all_html       = []
    by_folder      = defaultdict(list)
    district_pages = defaultdict(list)

    EXPECTED_SUBPAGES = [
        "index.html",
        "ard-process-guide.html",
        "evaluation-child-find.html",
        "grievance-dispute-resolution.html",
        "dyslexia-services.html",
        "leadership-directory.html",
    ]

    for root, dirs, files in os.walk(site_dir):
        dirs[:] = [d for d in dirs if not d.startswith(".") and d != "_canonical_backups" and d != "_trailing_slash_backups"]
        for f in files:
            if f.endswith(".html"):
                full = os.path.join(root, f)
                rel  = os.path.relpath(full, site_dir)
                all_html.append(rel)
                folder = os.path.relpath(root, site_dir)
                by_folder[folder].append(f)

                # Track district sub-pages
                parts = rel.replace("\\", "/").split("/")
                if len(parts) >= 2 and parts[0] == "districts":
                    district = parts[1] if len(parts) > 1 else "root"
                    district_pages[district].append(f)

    print(f"{'='*55}")
    print(f"  TOTAL HTML FILES FOUND: {len(all_html)}")
    print(f"  TOTAL FOLDERS WITH HTML: {len(by_folder)}")
    print(f"  DISTRICT FOLDERS: {len(district_pages)}")
    print(f"{'='*55}\n")

    # Show top level files
    print("TOP LEVEL FILES:")
    top = by_folder.get(".", [])
    for f in sorted(top):
        print(f"  {f}")
    print()

    # Check each district for missing sub-pages
    print("DISTRICT SUB-PAGE AUDIT:")
    print(f"  {'District':<35} {'Files Found':<15} {'Missing'}")
    print(f"  {'-'*70}")

    missing_count = 0
    complete_count = 0

    for district in sorted(district_pages.keys()):
        files   = district_pages[district]
        missing = [p for p in EXPECTED_SUBPAGES if p not in files]
        status  = "✓ Complete" if not missing else f"✗ Missing: {', '.join(missing)}"
        if missing:
            missing_count += 1
        else:
            complete_count += 1
        print(f"  {district:<35} {len(files):<15} {status}")

    print(f"\n  Complete districts  : {complete_count}")
    print(f"  Incomplete districts: {missing_count}")

    # Show folder breakdown
    print(f"\nFILES PER FOLDER (sample):")
    for folder, files in sorted(by_folder.items())[:10]:
        print(f"  {folder}/")
        for f in sorted(files):
            print(f"    - {f}")

    if len(by_folder) > 10:
        print(f"  ... and {len(by_folder) - 10} more folders")

    print()

if __name__ == "__main__":
    main()