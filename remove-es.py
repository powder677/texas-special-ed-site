import shutil
from pathlib import Path

# The main directory containing all your district folders
base_dir = Path(r"C:\Users\elisa\OneDrive\Documents\texas-special-ed-site\es-districts")

files_moved = 0

# Loop through every item in the base directory
for district_folder in base_dir.iterdir():
    # Check if the item is a folder (e.g., 'alvarado')
    if district_folder.is_dir():
        # Define the path to the 'es' subfolder
        es_folder = district_folder / "es"
        
        # If the 'es' subfolder exists, go inside it
        if es_folder.exists() and es_folder.is_dir():
            for file_path in es_folder.iterdir():
                if file_path.is_file():
                    # The destination is one level up (the district folder itself)
                    destination = district_folder / file_path.name
                    
                    # Prevent overwriting just in case
                    if destination.exists():
                        print(f"Warning: {destination.name} already exists in {district_folder.name}. Skipping.")
                        continue
                        
                    # Move the file
                    shutil.move(file_path, destination)
                    print(f"Moved: {file_path.name} --> {district_folder.name}\\")
                    files_moved += 1
            
            # Clean up: delete the 'es' folder now that it is empty
            try:
                es_folder.rmdir()
                print(f"Deleted empty folder: {es_folder.name} in {district_folder.name}")
            except OSError:
                print(f"Note: Could not delete {es_folder} (it might contain other folders).")

print(f"\nSuccess! Moved {files_moved} files to their staging district folders.")