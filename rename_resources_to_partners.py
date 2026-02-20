#!/usr/bin/env python3
"""
rename_resources_to_partners.py
================================
Renames resources.html → partners.html in every district subfolder.

USAGE:
  Dry run first:
    python rename_resources_to_partners.py --districts-dir "C:\\...\\districts" --dry-run

  Live run:
    python rename_resources_to_partners.py --districts-dir "C:\\...\\districts"
"""

import argparse
from pathlib import Path


def run(districts_dir: str, dry_run: bool):
    root = Path(districts_dir).resolve()

    if not root.exists():
        print(f"\nERROR: Directory not found: {root}\n")
        return

    print(f"\n{'='*60}")
    print(f"  Rename resources.html → partners.html")
    print(f"{'='*60}")
    print(f"  Root : {root}")
    print(f"  Mode : {'DRY RUN' if dry_run else 'LIVE'}")
    print(f"{'='*60}\n")

    targets = sorted(root.rglob("resources.html"))

    if not targets:
        print("  No resources.html files found.\n")
        return

    print(f"  Found {len(targets)} file(s) to rename:\n")

    renamed = 0
    skipped = 0
    errors  = []

    for f in targets:
        new_path = f.parent / "partners.html"
        rel      = f.relative_to(root)

        # Skip if partners.html already exists at that location
        if new_path.exists():
            print(f"  SKIP  {rel}  (partners.html already exists)")
            skipped += 1
            continue

        print(f"  {'WOULD RENAME' if dry_run else 'RENAMED'}  {rel}  →  partners.html")

        if not dry_run:
            try:
                f.rename(new_path)
                renamed += 1
            except Exception as e:
                errors.append(f"{rel}: {e}")
        else:
            renamed += 1

    print(f"\n{'='*60}")
    print(f"  Files renamed : {renamed}")
    print(f"  Skipped       : {skipped}")
    if errors:
        print(f"\n  Errors:")
        for e in errors:
            print(f"    {e}")
    print()
    if dry_run:
        print("  ℹ️  Dry run. Run without --dry-run to apply.")
    else:
        print("  ✅ Done.")
    print(f"{'='*60}\n")


if __name__ == "__main__":
    parser = argparse.ArgumentParser()
    parser.add_argument("--districts-dir", required=True)
    parser.add_argument("--dry-run", action="store_true")
    args = parser.parse_args()
    run(args.districts_dir, args.dry_run)