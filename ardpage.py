import os
import glob
from bs4 import BeautifulSoup
import copy

# ---------------------------------------------------------
# CONFIGURATION
# ---------------------------------------------------------
# The file that has your perfect layout (the one we just worked on)
MASTER_TEMPLATE_PATH = 'ard-process-guide.html' 

# The folder containing all 300+ of your other district files
# (e.g., 'districts/**/*.html')
TARGET_DIRECTORY = 'districts/' 

def standardize_layouts():
    print(f"Loading master template from {MASTER_TEMPLATE_PATH}...")
    
    try:
        with open(MASTER_TEMPLATE_PATH, 'r', encoding='utf-8') as f:
            master_soup = BeautifulSoup(f, 'html.parser')
    except FileNotFoundError:
        print("Master template not found! Please check the path.")
        return

    # Extract the perfect layout components we want to duplicate
    master_styles = master_soup.find_all('style')
    master_header = master_soup.find('header', class_='site-header')
    master_footer = master_soup.find('footer', class_='site-footer')
    
    # Optional: If you also want to standardize the inline bots/CTAs
    master_bots = master_soup.find_all('div', class_=lambda c: c and 'integrated-cta' in c)

    # Find strictly ARD-related files in the target directory
    search_pattern = os.path.join(TARGET_DIRECTORY, '**/*ard*.html')
    target_files = [f for f in glob.glob(search_pattern, recursive=True) if 'ard' in os.path.basename(f).lower()]
    
    print(f"Found {len(target_files)} files to process.")

    success_count = 0

    for filepath in target_files:
        # Skip the exact master file itself (not all files with the same name)
        if os.path.abspath(filepath) == os.path.abspath(MASTER_TEMPLATE_PATH):
            continue
            
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                target_soup = BeautifulSoup(f, 'html.parser')
                
            changed = False
            
            # 1. Update Styles
            # Remove old styles in the target
            for style in target_soup.find_all('style'):
                style.decompose()
            # Inject master styles into target <head>
            if target_soup.head:
                for style in reversed(master_styles):
                    target_soup.head.insert(len(target_soup.head.contents), copy.copy(style))
                changed = True
                
            # 2. Update Header (Navigation)
            target_header = target_soup.find('header', class_='site-header')
            if target_header and master_header:
                target_header.replace_with(copy.copy(master_header))
                changed = True
            elif not target_header and master_header and target_soup.body:
                # If target didn't have a header, insert it at the top of body
                target_soup.body.insert(0, copy.copy(master_header))
                changed = True
                
            # 3. Update Footer
            target_footer = target_soup.find('footer', class_='site-footer')
            if target_footer and master_footer:
                target_footer.replace_with(copy.copy(master_footer))
                changed = True
            elif not target_footer and master_footer and target_soup.body:
                # If target didn't have a footer, append it to body
                target_soup.body.append(copy.copy(master_footer))
                changed = True
                
            # 4. Save the standardized file
            if changed:
                with open(filepath, 'w', encoding='utf-8') as f:
                    # prettify() can sometimes mess up text formatting, 
                    # so we use standard string conversion
                    f.write(str(target_soup))
                success_count += 1
                
        except Exception as e:
            print(f"Error processing {filepath}: {e}")

    print(f"\nDone! Successfully standardized {success_count} files.")

if __name__ == "__main__":
    # Ensure BeautifulSoup is installed before running:
    # pip install beautifulsoup4
    standardize_layouts()