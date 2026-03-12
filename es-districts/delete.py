import os
import shutil

# Set to your directory, or '.' for current directory
base_path = '.' 

# The remaining folders, updated to capital letters
folders_to_delete = [
    "WIMBERLEY-ISD",
    "BROWNSBORO-ISD",
    "LIBERTY-ISD",
    "ROBSTOWN-ISD",
    "FARMERSVILLE-ISD",
    "NORTH-LAMAR-ISD",
    "ROBINSON-ISD"
]

def delete_remaining_folders():
    deleted_count = 0
    missing_count = 0

    print(f"Searching in base directory: {os.path.abspath(base_path)}\n")

    for folder_name in folders_to_delete:
        folder_path = os.path.join(base_path, folder_name)

        if os.path.exists(folder_path) and os.path.isdir(folder_path):
            try:
                shutil.rmtree(folder_path)
                print(f"[DELETED] {folder_name}")
                deleted_count += 1
            except Exception as e:
                print(f"[ERROR] Could not delete {folder_name}. Reason: {e}")
        else:
            print(f"[SKIPPED] {folder_name} (Does not exist or is not a directory)")
            missing_count += 1

    print("\n--- Summary ---")
    print(f"Successfully deleted: {deleted_count}")
    print(f"Skipped/Not found: {missing_count}")

if __name__ == "__main__":
    confirm = input(f"Delete these {len(folders_to_delete)} capitalized folders? (y/n): ")
    if confirm.lower() == 'y':
        delete_remaining_folders()
    else:
        print("Operation cancelled.")