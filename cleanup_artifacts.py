import os
from pathlib import Path

def clean_project(directory: str):
    """
    Recursively removes unnecessary artifact files from the project directory.
    """
    target_dir = Path(directory).resolve()
    
    # Define the extensions you want to purge
    extensions_to_remove = ['.bak', '.py']
    
    # Get the name of this script so it doesn't delete itself
    current_script = Path(__file__).resolve()
    
    deleted_count = 0
    
    print(f"Starting cleanup in: {target_dir}")
    print("-" * 40)
    
    for ext in extensions_to_remove:
        # rglob performs a recursive search for the given extension
        for file_path in target_dir.rglob(f'*{ext}'):
            if file_path.is_file() and file_path != current_script:
                try:
                    file_path.unlink()
                    print(f"Deleted: {file_path.relative_to(target_dir)}")
                    deleted_count += 1
                except PermissionError:
                    print(f"Permission denied: {file_path.name}")
                except Exception as e:
                    print(f"Error deleting {file_path.name}: {e}")
                    
    print("-" * 40)
    print(f"Cleanup complete. Successfully removed {deleted_count} files.")

if __name__ == "__main__":
    # '.' represents the current directory where the script is executed
    clean_project('.')