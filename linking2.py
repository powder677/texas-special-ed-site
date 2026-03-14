import os
import re

def enforce_html_on_district_links(directory_path):
    """
    Surgically finds links pointing to district pages that are missing the .html extension
    and safely adds it.
    """
    # REGEX BREAKDOWN:
    # (href=|"item":\s*) -> Group 1: Matches 'href=' or '"item": '
    # "                  -> Matches the opening quote
    # (                  -> Group 2 Start: The URL itself
    # [^"]*?             -> Matches anything up to 'districts' or 'es-districts'
    # (?:districts|es-districts)[^"]*? 
    # /[a-zA-Z0-9-]+     -> Matches the end of the URL ensuring it's just words/hyphens 
    #                       (Crucially, no '.' so it skips files that already have .html)
    # )                  -> Group 2 End
    # "                  -> Matches the closing quote
    pattern = re.compile(r'(href=|"item":\s*)"([^"]*?(?:districts|es-districts)[^"]*?/[a-zA-Z0-9-]+)"')
    
    files_updated = 0

    for root, _, files in os.walk(directory_path):
        for file in files:
            if file.endswith(".html"):
                filepath = os.path.join(root, file)
                
                with open(filepath, 'r', encoding='utf-8') as f:
                    content = f.read()
                
                # \1 restores href= or "item":
                # \2 restores the URL
                # .html" adds the missing extension and closing quote
                replacement = r'\1"\2.html"'
                new_content = pattern.sub(replacement, content)
                
                if new_content != content:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(new_content)
                    print(f"✅ Surgically added .html to links in: {filepath}")
                    files_updated += 1
                    
    print(f"\nDone! Fixed missing .html links in {files_updated} file(s).")

if __name__ == "__main__":
    target_directory = './' # Leave as './' to run in your current folder
    print(f"Scanning directory: {target_directory} ...")
    enforce_html_on_district_links(target_directory)