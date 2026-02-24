import os
from bs4 import BeautifulSoup

# 1. Configuration
DIRECTORY_TO_SEARCH = '.' 
NEW_AD_LINK = 'https://www.texasspecialed.com/advertise/index.html'

# 2. Add all your target button phrases here (must be lowercase)
TARGET_PHRASES = [
    'become a partner',
    'claim this category',
    'reserve this exclusive spot'
]

def update_ad_links(directory):
    files_updated = 0
    
    print("Scanning HTML files for ad placement buttons...")
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.html'):
                filepath = os.path.join(root, file)
                
                with open(filepath, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                    
                soup = BeautifulSoup(html_content, 'html.parser')
                file_was_modified = False
                
                # 3. Find all anchor <a> tags
                for a_tag in soup.find_all('a'):
                    link_text = a_tag.get_text(strip=True).lower()
                    
                    # 4. Check if ANY of our target phrases are inside the link text
                    if any(phrase in link_text for phrase in TARGET_PHRASES):
                        current_href = a_tag.get('href')
                        
                        # Only update and trigger a file save if the link needs changing
                        if current_href != NEW_AD_LINK:
                            a_tag['href'] = NEW_AD_LINK
                            file_was_modified = True
                
                # 5. Save the file if modifications were made
                if file_was_modified:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(str(soup))
                    print(f"  -> Updated links in: {filepath}")
                    files_updated += 1
                    
    print(f"\nDone! Successfully updated {files_updated} HTML files to point to {NEW_AD_LINK}.")

if __name__ == '__main__':
    update_ad_links(DIRECTORY_TO_SEARCH)