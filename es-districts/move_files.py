import os
import shutil
import re
import difflib

def main():
    # 1. Define the directory where your folders and loose files are
    base_dir = r"C:\Users\elisa\OneDrive\Documents\texas-special-ed-site\es-districts"

    # 2. Verify the directory exists
    if not os.path.exists(base_dir):
        print(f"Could not find the directory at: {base_dir}")
        return

    # 3. Get a list of all folders (directories) in the base_dir
    folders = [f for f in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, f))]

    # Helper function to normalize text so we can match filenames to folder names easily
    def normalize(name):
        name = name.lower()
        # Remove common extra words from the file name
        name = name.replace('como-solicitar-una-evaluacion-fie-en-', '')
        name = name.replace('.html', '')
        # Remove "texas" if it was added to the end of the URL/filename
        name = re.sub(r'-texas$', '', name)
        name = re.sub(r'texas$', '', name)
        # Remove all spaces, hyphens, and non-alphanumeric characters
        name = re.sub(r'[^a-z0-9]', '', name)
        return name

    # Create a dictionary to map the normalized folder name back to the ACTUAL folder name
    folder_mapping = {normalize(folder): folder for folder in folders}

    print("Scanning for files to move...\n")
    moved_count = 0

    # 4. Iterate through all items in the directory
    for file_name in os.listdir(base_dir):
        file_path = os.path.join(base_dir, file_name)
        
        # We only want to process files (not folders) that are HTML pages
        if os.path.isfile(file_path) and file_name.endswith('.html') and file_name.startswith('como-solicitar'):
            
            # Normalize the filename to figure out which district it belongs to
            norm_file = normalize(file_name)
            
            # 5. Try to find the matching folder
            best_match = None
            if norm_file in folder_mapping:
                best_match = folder_mapping[norm_file]
            else:
                # Fallback to fuzzy matching if the filename spelling is slightly off
                matches = difflib.get_close_matches(norm_file, list(folder_mapping.keys()), n=1, cutoff=0.75)
                if matches:
                    best_match = folder_mapping[matches[0]]
                    
            # 6. Move the file if a matching folder was found
            if best_match:
                destination_folder = os.path.join(base_dir, best_match)
                destination_path = os.path.join(destination_folder, file_name)
                
                try:
                    shutil.move(file_path, destination_path)
                    print(f"✅ Moved: '{file_name}'  -->  '/{best_match}/'")
                    moved_count += 1
                except Exception as e:
                    print(f"❌ Error moving '{file_name}': {e}")
            else:
                print(f"⚠️ Could not find a matching folder for file: '{file_name}'")

    print(f"\nSuccess! Moved {moved_count} files into their district folders.")

if __name__ == "__main__":
    main()