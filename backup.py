import os

# folder to clean
root_dir = r"C:\your\project\folder"

# backup file patterns
backup_extensions = [".bak", ".backup", ".old", ".tmp"]
backup_suffixes = ["~"]

deleted = 0

for root, dirs, files in os.walk(root_dir):
    for file in files:
        filepath = os.path.join(root, file)

        if any(file.endswith(ext) for ext in backup_extensions) or \
           any(file.endswith(suf) for suf in backup_suffixes):

            try:
                os.remove(filepath)
                deleted += 1
                print(f"Deleted: {filepath}")
            except Exception as e:
                print(f"Error deleting {filepath}: {e}")

print(f"\nTotal files deleted: {deleted}")