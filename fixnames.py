import os
from pathlib import Path

# Define your base directory
base_dir = Path(r"C:\Users\elisa\OneDrive\Documents\texas-special-ed-site\es-districts")
prefix = "como-solicitar-una-evaluacion-fie-en-"

# 1. Grab all the valid folder names so we know exactly what the district name should be
valid_folders = {d.name.lower(): d.name for d in base_dir.iterdir() if d.is_dir()}

files_renamed = 0
files_already_correct = 0

# 2. Find all the "como" files sitting in the main directory
for file_path in base_dir.glob(f"{prefix}*.html"):
    if not file_path.is_file():
        continue
        
    base_name = file_path.stem
    district_part = base_name.replace(prefix, "")
    
    # Strip the "-texas" off the end if the generator added it
    if district_part.endswith("-texas"):
        district_part = district_part[:-6]
        
    matched_folder = None
    
    # 3. Figure out which folder this file is supposed to map to
    if district_part in valid_folders:
        matched_folder = valid_folders[district_part]
    elif district_part.replace("-isd", "") in valid_folders:
        matched_folder = valid_folders[district_part.replace("-isd", "")]
    elif f"{district_part}-isd" in valid_folders:
        matched_folder = valid_folders[f"{district_part}-isd"]
        
    # 4. If we found a match, construct the PERFECT file name and rename it
    if matched_folder:
        new_file_name = f"{prefix}{matched_folder}.html"
        new_file_path = base_dir / new_file_name
        
        # Only rename it if the name actually needs to change
        if file_path.name != new_file_name:
            if not new_file_path.exists():
                file_path.rename(new_file_path)
                print(f"Renamed: {file_path.name}  -->  {new_file_name}")
                files_renamed += 1
            else:
                print(f"Skipped: {new_file_name} already exists. Might be a duplicate.")
        else:
            files_already_correct += 1
    else:
        print(f"⚠️ Warning: Could not find a matching folder for '{file_path.name}'. Leaving as is.")

print(f"\nSuccess! Renamed {files_renamed} files to match their exact district names. ({files_already_correct} were already perfect).")