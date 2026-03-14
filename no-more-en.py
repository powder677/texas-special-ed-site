import os
import re

def remove_injected_en(directory_path):
    """
    Removes the injected '-en-' from both the internal HTML links 
    and the physical file names.
    """
    files_updated = 0
    files_renamed = 0

    # Pattern to find the unwanted "-en-" in the text/links
    pattern = re.compile(r'como-solicitar-una-evaluacion-fie-en-([a-zA-Z0-9-]+)')

    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith(".html"):
                filepath = os.path.join(root, file)
                
                # 1. Fix the text/links inside the file
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Replace 'fie-en-district' with 'fie-district'
                new_content = pattern.sub(r'como-solicitar-una-evaluacion-fie-\1', content)
                
                if new_content != content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"✅ Removed '-en-' from links inside: {file}")
                    files_updated += 1
                
                # 2. Fix the actual file name on your hard drive if it was altered
                if "como-solicitar-una-evaluacion-fie-en-" in file:
                    new_name = file.replace("como-solicitar-una-evaluacion-fie-en-", "como-solicitar-una-evaluacion-fie-")
                    new_filepath = os.path.join(root, new_name)
                    os.rename(filepath, new_filepath)
                    print(f"🔄 Renamed file back to normal: {file}  ->  {new_name}")
                    files_renamed += 1

    print(f"\nDone! Updated text in {files_updated} file(s) and renamed {files_renamed} file(s).")

if __name__ == "__main__":
    target_directory = './' # Leave as './' to run in your current folder
    print(f"Scanning directory: {target_directory} ...")
    remove_injected_en(target_directory)