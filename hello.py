import os
import re

def fix_links_and_force_html(directory_path):
    """
    Scans files to fix the FIE evaluation links. 
    It replaces the wrong city name with the folder name AND 
    ensures the link ends with .html. It also adds .html to the file itself if missing.
    """
    # Regex pattern breakdown:
    # href="/districts/       -> Matches the start of the path
    # ([^/]+)                 -> Capture Group 1: The actual district folder (e.g., 'aldine-isd')
    # /es/como-solicitar...   -> Matches the middle of the path
    # [^/"]+"                 -> Matches whatever is at the end of the filename until the closing quote
    pattern = re.compile(r'href="/districts/([^/]+)/es/como-solicitar-una-evaluacion-fie-en-[^/"]+"')
    
    files_updated = 0

    # Walk through all directories and files
    for root, _, files in os.walk(directory_path):
        for file in files:
            # Catch files that end in .html OR the specific file missing the extension
            if file.endswith(".html") or "como-solicitar" in file:
                filepath = os.path.join(root, file)
                
                # Read the file
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # Replace the matched string and strictly enforce the .html extension inside the code
                replacement = r'href="/districts/\1/es/como-solicitar-una-evaluacion-fie-en-\1.html"'
                new_content = pattern.sub(replacement, content)
                
                # If changes were made, write them back to the file
                if new_content != content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"✅ Fixed links in: {filepath}")
                    files_updated += 1
                
                # FIX THE ACTUAL FILE NAME: Add .html to the file on your computer if it's missing
                if not file.endswith(".html"):
                    new_filepath = filepath + ".html"
                    os.rename(filepath, new_filepath)
                    print(f"🔄 Renamed file to include .html: {new_filepath}")
                    
    print(f"\nDone! Updated {files_updated} file(s).")

# --- How to run it ---
if __name__ == "__main__":
    target_directory = './' # Change this to your target directory path
    print(f"Scanning directory: {target_directory} ...")
    fix_links_and_force_html(target_directory)