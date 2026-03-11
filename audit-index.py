import os
import re

# Set the path to the specific district folder you want to check
district_folder = r"C:\Users\elisa\OneDrive\Documents\texas-special-ed-site\districts\greenville-isd"
index_file_path = os.path.join(district_folder, "index.html")

# 1. Get all HTML files in the folder, skipping the index itself
all_files = os.listdir(district_folder)
html_files = [f for f in all_files if f.endswith('.html') and f.lower() != 'index.html']

# 2. Read the current contents of the index.html
try:
    with open(index_file_path, 'r', encoding='utf-8') as f:
        index_content = f.read()
except FileNotFoundError:
    print(f"Error: Could not find index.html in {district_folder}")
    exit()

missing_files = []

# 3. Check if the filename exists anywhere in the index.html text
for html_file in html_files:
    if html_file not in index_content:
        missing_files.append(html_file)

# 4. Report the findings and generate smart cards
if not missing_files:
    print("✅ All good! Every HTML file is linked in the index.")
else:
    print(f"⚠️ Found {len(missing_files)} orphaned files without a card in the index:\n")
    
    for missing in missing_files:
        file_path = os.path.join(district_folder, missing)
        title = missing.replace('-', ' ').replace('.html', '').title() # Fallback title
        snippet = f"Click here to read more about {title.lower()}."    # Fallback snippet
        
        # Try to extract the real title and first paragraph from the file
        try:
            with open(file_path, 'r', encoding='utf-8') as f:
                content = f.read()
                
                # Regex to find <h1>...</h1>
                h1_match = re.search(r'<h1>(.*?)</h1>', content, re.IGNORECASE | re.DOTALL)
                if h1_match:
                    # Clean up any HTML tags inside the h1
                    title = re.sub(r'<[^>]+>', '', h1_match.group(1)).strip()
                
                # Regex to find the first <p>...</p>
                p_match = re.search(r'<p>(.*?)</p>', content, re.IGNORECASE | re.DOTALL)
                if p_match:
                    # Clean up HTML tags and truncate to ~120 characters
                    clean_p = re.sub(r'<[^>]+>', '', p_match.group(1)).strip()
                    snippet = clean_p[:120] + "..." if len(clean_p) > 120 else clean_p
        except Exception as e:
            pass # If it fails to read, it just uses the fallback title/snippet
            
        card_snippet = f"""
        <div class="resource-card">
            <h3><a href="{missing}">{title}</a></h3>
            <p>{snippet}</p>
        </div>
        """
        print(card_snippet)

print("\nAudit complete!")