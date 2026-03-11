import shutil
from pathlib import Path

def move_spanish_files():
    # Define your base directories
    source_dir = Path("districts")
    target_dir = Path("es-district")
    
    # We use a wildcard (*) in case the filename varies slightly by district
    # Update the extension to .html if needed, or leave the wildcard to catch all
    search_pattern = "como-solicitar-una-evaluacion-fie*"
    
    # Find all matching files in any subfolder of the 'districts' directory
    files_to_move = list(source_dir.rglob(search_pattern))
    
    if not files_to_move:
        print(f"No files found matching '{search_pattern}' in '{source_dir}'")
        return

    print(f"Found {len(files_to_move)} files to move. Starting process...\n")

    for source_path in files_to_move:
        # Extract the district folder name (e.g., 'abilene-isd' from 'districts/abilene-isd/file.html')
        district_name = source_path.parent.name
        
        # Create the new destination directory (e.g., 'es-district/abilene-isd')
        dest_folder = target_dir / district_name
        dest_folder.mkdir(parents=True, exist_ok=True)
        
        # Define the full destination path for the file
        dest_path = dest_folder / source_path.name
        
        try:
            # Move the file
            shutil.move(str(source_path), str(dest_path))
            print(f"✅ Moved: {source_path} -> {dest_path}")
        except Exception as e:
            print(f"❌ Error moving {source_path}: {e}")

    print("\nFile transfer complete!")

if __name__ == "__main__":
    move_spanish_files()