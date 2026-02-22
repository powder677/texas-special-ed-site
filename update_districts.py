import os
from bs4 import BeautifulSoup

# Base directory for the districts
BASE_DIR = r"C:\Users\elisa\OneDrive\Documents\texas-special-ed-site\districts"

# List of districts to process
DISTRICTS = [
    "garland-isd", 
    "frisco-isd", 
    "plano-isd", 
    "katy-isd", 
    "north-east-isd"
]

def process_districts():
    for district in DISTRICTS:
        district_path = os.path.join(BASE_DIR, district)
        
        if not os.path.exists(district_path):
            print(f"Directory not found, skipping: {district_path}")
            continue
            
        index_path = os.path.join(district_path, "index.html")
        updates_path = os.path.join(district_path, "special-ed-updates.html")
        
        # Ensure both files exist
        if not os.path.exists(index_path) or not os.path.exists(updates_path):
            print(f"Missing HTML files in {district} folder. Skipping.")
            continue

        # 1. Parse index.html to grab the correct navbar and footer
        with open(index_path, 'r', encoding='utf-8') as f:
            index_soup = BeautifulSoup(f, 'html.parser')
            
        std_header = index_soup.find('header', class_='site-header')
        std_footer = index_soup.find('footer', class_='site-footer')
        
        # 2. Update special-ed-updates.html
        with open(updates_path, 'r', encoding='utf-8') as f:
            updates_soup = BeautifulSoup(f, 'html.parser')
            
        # Replace Header
        old_header = updates_soup.find('header', class_='site-header')
        if old_header and std_header:
            old_header.replace_with(BeautifulSoup(str(std_header), 'html.parser'))
            print(f"[{district}] Updated navbar.")
            
        # Replace Footer
        old_footer = updates_soup.find('footer', class_='site-footer')
        if old_footer and std_footer:
            old_footer.replace_with(BeautifulSoup(str(std_footer), 'html.parser'))
            print(f"[{district}] Updated footer.")
            
        # Remove the ARD Power Pack sales card ($9.99)
        sales_cards = updates_soup.find_all('div', class_='sales-card')
        for card in sales_cards:
            text = card.get_text()
            # Searching for key phrases in case the district acronym (FISD, GISD, etc.) changes
            if "ARD Power Pack" in text or "$9.99" in text:
                card.decompose()
                print(f"[{district}] Removed $9.99 ARD Power Pack box.")
                
        # Save changes to special-ed-updates.html
        with open(updates_path, 'w', encoding='utf-8') as f:
            f.write(str(updates_soup))

        # 3. Add link to special-ed-updates.html inside index.html's grid (if missing)
        grid_links = index_soup.find('div', class_='grid-links')
        if grid_links:
            # Check if link is already there to avoid duplicates
            link_exists = any('special-ed-updates' in a.get('href', '') for a in grid_links.find_all('a'))
            
            if not link_exists:
                # Create the new link block
                new_link = index_soup.new_tag('a', href=f"/districts/{district}/special-ed-updates.html", attrs={"class": "resource-box"})
                
                h3 = index_soup.new_tag('h3')
                h3.string = "📰 Special Ed Updates"
                
                p = index_soup.new_tag('p')
                p.string = "Critical news, trends, and advocacy strategies for your district."
                
                new_link.append(h3)
                new_link.append(p)
                
                # Append to the grid
                grid_links.append(new_link)
                
                # Save changes to index.html
                with open(index_path, 'w', encoding='utf-8') as f:
                    f.write(str(index_soup))
                print(f"[{district}] Linked 'special-ed-updates.html' to index grid.")
        
        print("-" * 40)

if __name__ == "__main__":
    print("Starting batch update...\n")
    process_districts()
    print("Update complete!")