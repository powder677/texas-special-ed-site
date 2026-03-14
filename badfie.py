import os
import re

def fix_district_links(directory_path):
    """
    Scans HTML files in a directory and fixes broken FIE evaluation links
    by replacing the wrong city name in the file name with the actual district 
    name from the folder path.
    """
    # Regex pattern breakdown:
    # href="/districts/      -> Matches the start of the path
    # ([^/]+)                -> Capture Group 1: The actual district folder (e.g., 'aldine-isd')
    # /es/como-solicitar...  -> Matches the middle of the path
    # [^/"]+\.html"          -> Matches the incorrect trailing filename until the closing quote
    pattern = re.compile(r'href="/districts/([^/]+)/es/como-solicitar-una-evaluacion-fie-en-[^/"]+\.html"')
    
    files_updated = 0

    # Walk through all directories and files
    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith(".html"):
                filepath = os.path.join(root, file)
                
                # Read the file
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Replace the matched string
                # \1 drops in the captured folder name (e.g., 'aldine-isd') into the filename
                replacement = r'href="/districts/\1/es/como-solicitar-una-evaluacion-fie-en-\1.html"'
                new_content = pattern.sub(replacement, content)
                
                # If changes were made, write them back to the file
                if new_content != content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"✅ Fixed links in: {filepath}")
                    files_updated += 1
                    
    print(f"\nDone! Updated {files_updated} file(s).")

# --- How to run it ---
# Point this to the root folder where your HTML files are stored
if __name__ == "__main__":
    target_directory = './' # Change this to your target directory path
    print(f"Scanning directory: {target_directory} ...")
    fix_district_links(target_directory)