import os
import re

# Set the directory where your HTML files are located. 
# '.' means the current folder where the script is running.
DIRECTORY = '.'

def format_blog_pages(directory):
    # Regex to find <style> blocks that contain '.page-grid'
    # This safely deletes the conflicting layout styles without touching other potential style blocks
    style_pattern = re.compile(r'<style>[\s\S]*?\.page-grid[\s\S]*?</style>', re.IGNORECASE)

    updated_count = 0

    # Walk through all directories, subdirectories, and files
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.html'):
                filepath = os.path.join(root, file)
                
                try:
                    with open(filepath, 'r', encoding='utf-8') as f:
                        content = f.read()

                    original_content = content

                    # 1. Update main column class
                    content = content.replace('class="main-content-col"', 'class="main-col"')
                    
                    # 2. Update layout grid wrapper
                    content = content.replace('class="layout-grid"', 'class="page-grid"')
                    
                    # 3. Strip the conflicting inline <style> block
                    content = style_pattern.sub('', content)

                    # Only save if changes were actually made
                    if content != original_content:
                        with open(filepath, 'w', encoding='utf-8') as f:
                            f.write(content)
                        print(f"✅ Updated: {filepath}")
                        updated_count += 1
                    else:
                        print(f"⏭️ Skipped (already clean): {filepath}")
                
                except Exception as e:
                    print(f"❌ Error reading {filepath}: {e}")

    print(f"\n🎉 Finished! Successfully updated {updated_count} files.")

if __name__ == '__main__':
    print("Starting HTML formatting scan...\n")
    format_blog_pages(DIRECTORY)