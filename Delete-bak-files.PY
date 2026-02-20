import os
import glob

# Find all .bak files recursively from the current directory
bak_files = glob.glob("**/*.bak", recursive=True) + glob.glob("*.bak")

if not bak_files:
    print("No .bak files found.")
else:
    print(f"Found {len(bak_files)} .bak file(s):\n")
    for filepath in bak_files:
        try:
            os.remove(filepath)
            print(f"  Deleted: {filepath}")
        except OSError as e:
            print(f"  ERROR deleting {filepath}: {e}")

    print(f"\nDone. {len(bak_files)} file(s) removed.")