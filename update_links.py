import os
from bs4 import BeautifulSoup

# 1. Configuration
DIRECTORY_TO_SEARCH = '.' 
# Updated to the exact path
NEW_AD_LINK = 'https://www.texasspecialed.com/advertise/index.html' 

def update_partner_links(directory):
    files_updated = 0
    
    print("Scanning HTML files for 'Become a Partner' buttons...")
    
    for root, dirs, files in os.walk(directory):
        for file in files:
            if file.endswith('.html'):
                filepath = os.path.join(root, file)
                
                with open(filepath, 'r', encoding='utf-8') as f:
                    html_content = f.read()
                    
                soup = BeautifulSoup(html_content, 'html.parser')
                file_was_modified = False
                
                for a_tag in soup.find_all('a'):
                    link_text = a_tag.get_text(strip=True).lower()
                    
                    if 'become a partner' in link_text:
                        current_href = a_tag.get('href')
                        
                        if current_href != NEW_AD_LINK:
                            a_tag['href'] = NEW_AD_LINK
                            file_was_modified = True
                
                if file_was_modified:
                    with open(filepath, 'w', encoding='utf-8') as f:
                        f.write(str(soup))
                    print(f"  -> Updated links in: {filepath}")
                    files_updated += 1
                    
    print(f"\nDone! Successfully updated {files_updated} HTML files to point to {NEW_AD_LINK}.")

if __name__ == '__main__':
    update_partner_links(DIRECTORY_TO_SEARCH)