import os
import glob
from bs4 import BeautifulSoup

# Define your exact paths
BASE_DIR = r"C:\Users\elisa\OneDrive\Documents\texas-special-ed-site"
BLOG_DIR = os.path.join(BASE_DIR, "blog")

# We will use the FIE timeline article as the source of truth for the perfect header/footer
MASTER_FILE = os.path.join(BLOG_DIR, "fie-evaluation-timeline.html")

def sync_headers_footers():
    print(f"Looking for master template at: {MASTER_FILE}")
    if not os.path.exists(MASTER_FILE):
        print("❌ Master file not found. Please check the file path.")
        return

    # 1. Extract the perfect header and footer from the master file
    with open(MASTER_FILE, 'r', encoding='utf-8') as f:
        master_soup = BeautifulSoup(f, 'html.parser')
        
    master_header = master_soup.find('header', class_='site-header')
    master_footer = master_soup.find('footer', class_='site-footer')

    if not master_header or not master_footer:
        print("❌ Could not locate the <header class='site-header'> or <footer class='site-footer'> in the master file.")
        return

    print("✅ Master header and footer extracted successfully.\n")

    # 2. Find all HTML files in the blog folder
    html_files = glob.glob(os.path.join(BLOG_DIR, "*.html"))
    updated_count = 0

    # 3. Iterate through every blog post
    for file_path in html_files:
        filename = os.path.basename(file_path)
        
        # Skip the master file so we don't overwrite it with itself
        if file_path == MASTER_FILE:
            continue
            
        print(f"Processing: {filename}...")
        
        with open(file_path, 'r', encoding='utf-8') as f:
            soup = BeautifulSoup(f, 'html.parser')

        changed = False
        
        # 4. Swap the old header for the new one
        old_header = soup.find('header', class_='site-header')
        if old_header:
            old_header.replace_with(master_header)
            changed = True
        elif soup.body:
            # If the file is missing a header entirely, insert it at the top of the body
            soup.body.insert(0, master_header)
            changed = True

        # 5. Swap the old footer for the new one
        old_footer = soup.find('footer', class_='site-footer')
        if old_footer:
            old_footer.replace_with(master_footer)
            changed = True
        elif soup.body:
            # If the file is missing a footer entirely, add it to the bottom of the body
            soup.body.append(master_footer)
            changed = True

        # 6. Save the updated file securely
        if changed:
            try:
                with open(file_path, 'w', encoding='utf-8') as f:
                    # str() converts the BeautifulSoup object back to clean HTML
                    f.write(str(soup))
                print(f"  -> ✅ Updated {filename}")
                updated_count += 1
            except PermissionError:
                print(f"  -> ❌ Permission denied. OneDrive is likely syncing {filename}. Wait a moment or pause sync, then try again.")
        else:
            print(f"  -> ⚠️ No changes needed for {filename}")

    print(f"\n🎉 Done! Successfully synced the navbar and footer across {updated_count} blog posts.")

if __name__ == "__main__":
    sync_headers_footers()