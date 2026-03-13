from pathlib import Path

def count_files_in_subfolders(target_directory):
    # This takes the path you provide at the bottom and preps it
    base_path = Path(target_directory)
    
    # Check if the path actually exists to avoid errors
    if not base_path.exists() or not base_path.is_dir():
        print(f"Error: The directory '{target_directory}' does not exist.")
        return

    print(f"Scanning folders in: {base_path}\n" + "-"*40)
    
    folder_count = 0
    
    # Loop through everything inside the base folder
    for folder in base_path.iterdir():
        # Make sure we are only looking at directories (folders)
        if folder.is_dir():
            folder_count += 1
            # Count how many items inside are actually files (ignores sub-sub-folders)
            file_count = sum(1 for item in folder.iterdir() if item.is_file())
            
            # Print the result
            print(f"Folder: {folder.name} | Contains: {file_count} files")
            
    print("-" * 40)
    print(f"Total folders scanned: {folder_count}")

# --- Your Folder Path goes here! ---
# Notice the 'r' before the quotes, which keeps the Windows backslashes safe.
main_folder_path = r"C:\Users\elisa\OneDrive\Documents\texas-special-ed-site\es-districts" 

# This runs the function using your path
count_files_in_subfolders(main_folder_path)