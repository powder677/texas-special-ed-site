"""
Restore all what-is-fie.html files from a specific commit
"""

import subprocess
import os
from pathlib import Path

os.chdir(r"C:\Users\elisa\OneDrive\Documents\texas-special-ed-site")

# The commit that has the what-is-fie.html files
COMMIT_HASH = "df36c756"

print("=" * 60)
print("RESTORING what-is-fie.html FILES")
print("=" * 60)
print()

# Find all what-is-fie.html files that exist in that commit
print(f"Finding what-is-fie.html files in commit {COMMIT_HASH}...")

result = subprocess.run(
    ["git", "ls-tree", "-r", "--name-only", COMMIT_HASH],
    capture_output=True, text=True, shell=True
)

if result.returncode != 0:
    print("Error: Could not read commit")
    exit(1)

# Filter for what-is-fie.html files
all_files = result.stdout.strip().split('\n')
fie_files = [f for f in all_files if f.endswith('what-is-fie.html') and f.startswith('districts/')]

print(f"Found {len(fie_files)} what-is-fie.html files")
print()

if not fie_files:
    print("No what-is-fie.html files found in that commit!")
    exit(1)

# Show first few
print("Files to restore:")
for f in fie_files[:5]:
    print(f"  {f}")
if len(fie_files) > 5:
    print(f"  ... and {len(fie_files) - 5} more")
print()

# Ask for confirmation
response = input(f"Restore all {len(fie_files)} files from commit {COMMIT_HASH}? (yes/no): ")
if response.lower() != 'yes':
    print("Cancelled.")
    exit(0)

print()
print("Restoring files...")

# Restore each file
success_count = 0
failed_count = 0

for file_path in fie_files:
    result = subprocess.run(
        ["git", "checkout", COMMIT_HASH, "--", file_path],
        capture_output=True, text=True, shell=True
    )
    
    if result.returncode == 0:
        success_count += 1
        if success_count <= 3:
            print(f"  ✓ {file_path}")
    else:
        failed_count += 1
        print(f"  ✗ FAILED: {file_path}")

if success_count > 3:
    print(f"  ✓ ... and {success_count - 3} more files restored")

print()
print("=" * 60)
print(f"✓ Successfully restored: {success_count} files")
if failed_count > 0:
    print(f"✗ Failed: {failed_count} files")
print("=" * 60)
print()

if success_count > 0:
    print("Next step: Commit the changes")
    print("  git add districts/")
    print('  git commit -m "Restored what-is-fie.html files"')