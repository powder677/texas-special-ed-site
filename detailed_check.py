"""
Check if district files are actually damaged and if Git has old versions
"""

import os
import subprocess
from pathlib import Path

project_folder = r"C:\Users\elisa\OneDrive\Documents\texas-special-ed-site"
os.chdir(project_folder)

print("=" * 60)
print("DETAILED FILE RECOVERY CHECK")
print("=" * 60)
print()

# Check 1: Are the files actually damaged?
print("1. Checking if district files are actually damaged...")
districts_folder = Path("districts")

if not districts_folder.exists():
    print("   ✗ districts/ folder doesn't exist!")
    exit(1)

html_files = list(districts_folder.rglob("*.html"))
print(f"   Found {len(html_files)} HTML files in districts/")

# Check a few file sizes
damaged_count = 0
for file in html_files[:5]:
    size = file.stat().st_size
    status = "✗ DAMAGED" if size < 1000 else "✓ OK"
    print(f"   {status}: {file.name} ({size:,} bytes)")
    if size < 1000:
        damaged_count += 1

print()

# Check 2: Are these files tracked in Git?
print("2. Checking if district files are tracked in Git...")
result = subprocess.run(
    ["git", "ls-files", "districts/"],
    capture_output=True, text=True, shell=True
)

tracked_files = result.stdout.strip().split('\n') if result.stdout.strip() else []

if tracked_files and tracked_files != ['']:
    print(f"   ✓ {len(tracked_files)} files are tracked in Git")
    for file in tracked_files[:5]:
        print(f"      {file}")
    if len(tracked_files) > 5:
        print(f"      ... and {len(tracked_files) - 5} more")
else:
    print("   ✗ NO district files are tracked in Git")
    print("   → Git recovery won't work!")
    print("   → Must use VS Code Timeline")
    exit(1)

print()

# Check 3: Does Git have older versions?
print("3. Checking Git history for one file...")
if tracked_files:
    test_file = tracked_files[0]
    result = subprocess.run(
        ["git", "log", "--oneline", "-5", "--", test_file],
        capture_output=True, text=True, shell=True
    )
    
    if result.stdout.strip():
        print(f"   ✓ Git has history for {test_file}:")
        for line in result.stdout.strip().split('\n'):
            print(f"      {line}")
    else:
        print(f"   ✗ No history found for {test_file}")

print()

# Check 4: Show content from previous commit
print("4. Checking if previous commit has content...")
if tracked_files:
    test_file = tracked_files[0]
    result = subprocess.run(
        ["git", "show", f"HEAD:{test_file}"],
        capture_output=True, text=True, shell=True
    )
    
    if result.returncode == 0:
        old_content_size = len(result.stdout)
        print(f"   ✓ Previous version of {test_file}: {old_content_size:,} characters")
        
        # Check current file size
        current_size = Path(test_file).stat().st_size
        print(f"   Current version: {current_size:,} bytes")
        
        if old_content_size > current_size:
            print("   → Previous version is LARGER (has content!)")
            print("   → Git recovery WILL WORK!")
        else:
            print("   → Previous version same or smaller")
    else:
        print(f"   ✗ Could not retrieve previous version")

print()

# Check 5: Look at older commits
print("5. Checking older commits (going back in time)...")
result = subprocess.run(
    ["git", "log", "--all", "--oneline", "-10"],
    capture_output=True, text=True, shell=True
)

if result.stdout.strip():
    commits = result.stdout.strip().split('\n')
    print(f"   Found {len(commits)} recent commits:")
    for commit in commits:
        print(f"      {commit}")
    
    print()
    print("   Try restoring from an older commit:")
    first_commit = commits[1].split()[0] if len(commits) > 1 else commits[0].split()[0]
    print(f"   git checkout {first_commit} -- districts/")

print()
print("=" * 60)
print("FINAL RECOMMENDATION:")
print("=" * 60)
print()

if tracked_files and tracked_files != ['']:
    print("Your district files ARE in Git.")
    print()
    print("Try these recovery commands in order:")
    print()
    print("1. Restore from HEAD (last commit):")
    print("   git checkout HEAD -- districts/")
    print()
    print("2. If that doesn't work, restore from previous commit:")
    if result.stdout.strip():
        commits = result.stdout.strip().split('\n')
        if len(commits) > 1:
            prev_commit = commits[1].split()[0]
            print(f"   git checkout {prev_commit} -- districts/")
    print()
    print("3. If still nothing, the damage was committed to Git.")
    print("   You'll need to find a commit BEFORE the damage.")
    print("   Run: git log --oneline")
    print("   Then: git checkout <commit-hash> -- districts/")
else:
    print("Git recovery won't work.")
    print("Use VS Code Timeline for all files.")