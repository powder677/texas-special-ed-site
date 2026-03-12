import shutil
from pathlib import Path

# Define your source and destination paths using raw strings (r"") for Windows paths
source_dir = Path(r"C:\Users\elisa\OneDrive\Documents\texas-special-ed-site\es-district")
dest_dir = Path(r"C:\Users\elisa\OneDrive\Documents\texas-special-ed-site\es-districts")

# Create the destination directory if it doesn't already exist
dest_dir.mkdir(parents=True, exist_ok=True)

files_copied = 0

# rglob('*') searches recursively through all subfolders in the source directory
for file_path in source_dir.rglob('*'):
    # Check if the current path is a file (and not a folder)
    if file_path.is_file():
        dest_file_path = dest_dir / file_path.name
        
        # Prevent overwriting if a file with the same name already exists in the destination
        counter = 1
        while dest_file_path.exists():
            new_name = f"{file_path.stem}_{counter}{file_path.suffix}"
            dest_file_path = dest_dir / new_name
            counter += 1
            
        # Copy the file to the new location (preserves metadata)
        shutil.copy2(file_path, dest_file_path)
        print(f"Copied: {file_path.name} --> {dest_file_path.name}")
        files_copied += 1

print(f"\nSuccess! Copied a total of {files_copied} files to {dest_dir}")