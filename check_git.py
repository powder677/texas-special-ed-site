"""
Quick Git Diagnostic - Check if files can be recovered via Git
"""

import subprocess
import os

project_folder = r"C:\Users\elisa\OneDrive\Documents\texas-special-ed-site"

print("=" * 60)
print("GIT RECOVERY DIAGNOSTIC")
print("=" * 60)
print()

# Change to project directory
try:
    os.chdir(project_folder)
    print(f"✓ Changed to: {os.getcwd()}")
except:
    print(f"✗ Could not access: {project_folder}")
    exit(1)

print()

# Check 1: Is this a Git repository?
print("1. Checking if this is a Git repository...")
result = subprocess.run(["git", "rev-parse", "--git-dir"], 
                       capture_output=True, text=True, shell=True)
if result.returncode == 0:
    print(f"   ✓ Yes! Git folder found at: {result.stdout.strip()}")
else:
    print("   ✗ NOT a Git repository")
    print("   → Git recovery won't work")
    print("   → Use VS Code Timeline instead")
    exit(1)

print()

# Check 2: Are there any commits?
print("2. Checking Git history...")
result = subprocess.run(["git", "log", "--oneline", "-5"], 
                       capture_output=True, text=True, shell=True)
if result.returncode == 0 and result.stdout.strip():
    print("   ✓ Found commits:")
    for line in result.stdout.strip().split('\n')[:3]:
        print(f"      {line}")
else:
    print("   ✗ No commits found")
    print("   → Git recovery won't work (nothing to restore from)")
    exit(1)

print()

# Check 3: What files changed?
print("3. Checking what Git sees as changed...")
result = subprocess.run(["git", "status", "--short"], 
                       capture_output=True, text=True, shell=True)
changed_files = result.stdout.strip().split('\n') if result.stdout.strip() else []

if not changed_files or changed_files == ['']:
    print("   ✗ Git doesn't see any changes")
    print("   → The files were never committed to Git")
    print("   → Use VS Code Timeline instead")
else:
    print(f"   ✓ Git sees {len(changed_files)} changed files:")
    for line in changed_files[:10]:
        print(f"      {line}")
    if len(changed_files) > 10:
        print(f"      ... and {len(changed_files) - 10} more")

print()

# Check 4: Can we see the old content?
print("4. Testing if Git has the old content...")
result = subprocess.run(["git", "diff", "--stat", "HEAD"], 
                       capture_output=True, text=True, shell=True)
if result.stdout.strip():
    print("   ✓ Git can show differences! Recovery is possible!")
    print()
    print("   Run this command to restore:")
    print("   git checkout HEAD -- districts/")
else:
    print("   ✗ No differences found in Git")

print()
print("=" * 60)
print("RECOMMENDATION:")
print("=" * 60)

if changed_files and changed_files != ['']:
    print("✓ Git recovery SHOULD work")
    print()
    print("Try this command:")
    print("   git restore districts/")
    print()
    print("Or:")
    print("   git checkout -- districts/")
    print()
    print("(without 'HEAD')")
else:
    print("✗ Git recovery WON'T work")
    print()
    print("Your files were never committed to Git.")
    print("Use VS Code Timeline instead:")
    print("  1. Right-click damaged file")
    print("  2. Open Timeline")
    print("  3. Restore previous version")