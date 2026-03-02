import os
import re

# Set your exact base directory path for the ENTIRE site
BASE_DIR = r"C:\Users\elisa\OneDrive\Documents\texas-special-ed-site"

# The new sleek text logo HTML
NEW_LOGO_HTML = r"""<div class="nav-logo">
<a aria-label="Texas Special Ed Home" href="/" class="text-logo">
Texas <em>Special Ed</em>
</a>
</div>"""

# This regex finds the <div class="nav-logo"> block and everything inside it
LOGO_REGEX = re.compile(r'<div\s+class=["\']nav-logo["\']>.*?</div>', re.IGNORECASE | re.DOTALL)

def main():
    if not os.path.exists(BASE_DIR):
        print(f"Error: Could not find directory at {BASE_DIR}")
        return

    count = 0

    # Walk through EVERY file in your website directory
    for root, dirs, files in os.walk(BASE_DIR):
        for file in files:
            if file.endswith(".html"):
                filepath = os.path.join(root, file)
                
                try:
                    with open(filepath, 'r', encoding='utf-8', errors='ignore') as f:
                        content = f.read()

                    # Only update if the old nav-logo block is found
                    if LOGO_REGEX.search(content):
                        # Replace the old block with the new text logo block
                        new_content = LOGO_REGEX.sub(NEW_LOGO_HTML, content)
                        
                        # Save the file if changes were made
                        if new_content != content:
                            with open(filepath, 'w', encoding='utf-8') as f:
                                f.write(new_content)
                            count += 1
                            print(f"Updated Logo in: {os.path.relpath(filepath, BASE_DIR)}")
                            
                except Exception as e:
                    print(f"Skipped {filepath}: {e}")

    print(f"\nSuccess! Replaced the logo with Large Fancy Text on {count} pages.")

if __name__ == "__main__":
    main()