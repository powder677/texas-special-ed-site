import os
import shutil

# Set your base directory
base_dir = r"C:\Users\elisa\OneDrive\Documents\texas-special-ed-site\districts"

# Get all directories in the base path
all_dirs = [d for d in os.listdir(base_dir) if os.path.isdir(os.path.join(base_dir, d))]

for dir_name in all_dirs:
    # Look for the folders that have the '-isd' suffix
    if dir_name.endswith('-isd'):
        # The corresponding original folder name would be the same, minus '-isd'
        base_name = dir_name[:-4] 
        
        source_dir = os.path.join(base_dir, base_name)
        target_dir = os.path.join(base_dir, dir_name)
        
        # Check if the original folder without '-isd' actually exists
        if os.path.exists(source_dir) and os.path.isdir(source_dir):
            print(f"Found matching pair: '{base_name}' -> '{dir_name}'")
            
            # Go through everything in the source folder
            for item in os.listdir(source_dir):
                # Skip the index.html file
                if item.lower() == 'index.html':
                    continue
                    
                source_item = os.path.join(source_dir, item)
                target_item = os.path.join(target_dir, item)
                
                # Move the file (or subfolder) to the -isd folder
                print(f"  Moving: {item}")
                shutil.move(source_item, target_item)
                
            print(f"Finished moving files for {base_name}.\n")

print("All done!")