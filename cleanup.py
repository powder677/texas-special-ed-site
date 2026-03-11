import os
import sys

def clean_up_folder(directory_path):
    print("=========================================================")
    print("🚨 WARNING: DESTRUCTIVE ACTION 🚨")
    print(f"This will delete ALL '.py' and '.bak' files in:\n{os.path.abspath(directory_path)}")
    print("This includes all of your generation scripts!")
    print("=========================================================")
    
    # Safety check so you don't accidentally wipe your tools
    confirm = input("Type 'YES' (all caps) to confirm and delete: ")
    
    if confirm != "YES":
        print("Aborted. No files were deleted.")
        sys.exit()

    # The name of THIS script so it doesn't delete itself while running
    this_script = os.path.basename(__file__)
    
    files_deleted = 0
    errors = 0

    # Walk through the directory and all subdirectories
    for root, dirs, files in os.walk(directory_path):
        # Optional: Skip your git or backups folder to be safe
        if '.git' in root or '_backups' in root:
            continue
            
        for file in files:
            if file.endswith('.py') or file.endswith('.bak'):
                # Don't delete the cleanup script itself
                if file == this_script:
                    continue
                    
                file_path = os.path.join(root, file)
                
                try:
                    os.remove(file_path)
                    print(f"🗑️ Deleted: {file_path}")
                    files_deleted += 1
                except Exception as e:
                    print(f"❌ Error deleting {file_path}: {e}")
                    errors += 1

    print("\n--- Cleanup Summary ---")
    print(f"Total files deleted: {files_deleted}")
    if errors > 0:
        print(f"Errors encountered: {errors}")

if __name__ == "__main__":
    # '.' means current directory
    project_dir = '.'
    clean_up_folder(project_dir)