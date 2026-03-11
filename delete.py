import os
import shutil
import stat

def remove_readonly(func, path, exc_info):
    """Error handler to clear the read-only attribute and retry."""
    os.chmod(path, stat.S_IWRITE)
    func(path)

# Set your base directory
base_dir = r"C:\Users\elisa\OneDrive\Documents\texas-special-ed-site\districts"

# Get all items in the base directory
all_items = os.listdir(base_dir)

for item in all_items:
    # Look for the folders that HAVE the '-isd' suffix
    if item.endswith('-isd') and os.path.isdir(os.path.join(base_dir, item)):
        # Determine the name of the original folder (without '-isd')
        original_folder_name = item[:-4]
        original_folder_path = os.path.join(base_dir, original_folder_name)
        
        # Check if that original folder exists
        if os.path.exists(original_folder_path) and os.path.isdir(original_folder_path):
            print(f"Deleting old folder: '{original_folder_name}'...")
            
            try:
                # shutil.rmtree with onexc handles the read-only error
                shutil.rmtree(original_folder_path, onexc=remove_readonly)
                print(f"Successfully deleted '{original_folder_name}'.")
            except Exception as e:
                print(f"Still couldn't delete {original_folder_name}. You may need to close File Explorer or pause OneDrive. Error: {e}")

print("\nCleanup complete!")