import os
import shutil
from pathlib import Path

# ======================================================================
# CONFIGURATION
# ======================================================================
# Set this to your project path, or use "." for the current directory
TARGET_DIR = "." 

# The file extensions you want to purge
EXTENSIONS_TO_DELETE = {
    '.bak',      # Backup files
    '.tmp',      # Temporary files
    '.pyc',      # Compiled Python files
    '.log',      # Log files
    '.DS_Store', # Mac OS clutter (if applicable)
    '.swp'       # Swap files from text editors
}

# Specific folders you want to delete entirely
DIRS_TO_DELETE = {
    '__pycache__',
    '.pytest_cache'
}

# ⚠️ SAFETY SWITCH ⚠️
# True = Only print what WOULD be deleted. 
# False = ACTUALLY delete the files.
DRY_RUN = False

def clean_project(directory):
    target_path = Path(directory)
    
    if not target_path.exists() or not target_path.is_dir():
        print(f"❌ Error: The directory {directory} does not exist.")
        return

    print(f"🧹 Starting cleanup in: {target_path.resolve()}")
    if DRY_RUN:
        print("🛡️  DRY RUN MODE IS ON: No files will actually be deleted.\n")
    else:
        print("⚠️  DANGER MODE: Files are being deleted.\n")

    files_deleted = 0
    dirs_deleted = 0
    bytes_freed = 0

    # Walk through the directory from the bottom up
    for root, dirs, files in os.walk(target_path, topdown=False):
        current_dir = Path(root)

        # 1. Check and delete individual files
        for file in files:
            file_path = current_dir / file
            if file_path.suffix in EXTENSIONS_TO_DELETE:
                file_size = file_path.stat().st_size
                
                if DRY_RUN:
                    print(f"[WOULD DELETE FILE] {file_path}")
                else:
                    try:
                        file_path.unlink()
                        print(f"[DELETED] {file_path}")
                    except Exception as e:
                        print(f"[ERROR] Could not delete {file_path}: {e}")
                        continue
                
                files_deleted += 1
                bytes_freed += file_size

        # 2. Check and delete specific directories (like __pycache__)
        for d in dirs:
            if d in DIRS_TO_DELETE:
                dir_path = current_dir / d
                
                if DRY_RUN:
                    print(f"[WOULD DELETE DIR]  {dir_path}")
                else:
                    try:
                        shutil.rmtree(dir_path)
                        print(f"[DELETED DIR] {dir_path}")
                    except Exception as e:
                        print(f"[ERROR] Could not delete directory {dir_path}: {e}")
                        continue
                
                dirs_deleted += 1

    # Print Summary
    print("\n" + "="*40)
    print("✨ CLEANUP SUMMARY ✨")
    print("="*40)
    if DRY_RUN:
        print("Note: This was a dry run. Change DRY_RUN = False to execute.")
    print(f"Files targeted:       {files_deleted}")
    print(f"Directories targeted: {dirs_deleted}")
    print(f"Space to free:        {bytes_freed / (1024*1024):.2f} MB")
    print("="*40)

if __name__ == "__main__":
    clean_project(TARGET_DIR)