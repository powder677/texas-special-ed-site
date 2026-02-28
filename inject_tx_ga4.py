import os
from bs4 import BeautifulSoup

# ==========================================
# CONFIGURATION
# ==========================================
SITE_ROOT_DIR = r"C:\Users\elisa\OneDrive\Documents\texas-special-ed-site"

GA4_SNIPPET = """
<script async src="https://www.googletagmanager.com/gtag/js?id=G-GVLPE273XH"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){dataLayer.push(arguments);}
  gtag('js', new Date());

  gtag('config', 'G-GVLPE273XH');
</script>
"""

def inject_ga4_code(root_dir):
    updated_count = 0
    
    for dirpath, _, filenames in os.walk(root_dir):
        for filename in filenames:
            if filename.endswith(".html"):
                file_path = os.path.join(dirpath, filename)
                
                try:
                    with open(file_path, 'r', encoding='utf-8') as file:
                        content = file.read()
                    
                    # Skip if your specific Texas GA4 tag is already there
                    if "G-GVLPE273XH" in content:
                        continue
                        
                    soup = BeautifulSoup(content, 'html.parser')
                    
                    # Ensure the file actually has a <head> tag before trying to insert
                    if soup.head:
                        # Convert snippet string to a BeautifulSoup object
                        snippet_soup = BeautifulSoup(GA4_SNIPPET, 'html.parser')
                        
                        # Insert right at the top of the <head> section (Best Practice for GA4)
                        soup.head.insert(0, snippet_soup)
                        
                        # Save back as string to preserve exact formatting (noprettify)
                        with open(file_path, 'w', encoding='utf-8') as file:
                            file.write(str(soup))
                        
                        print(f"✅ Injected GA4 into: {file_path}")
                        updated_count += 1
                    else:
                        print(f"⚠ No <head> found in {file_path}. Skipping.")
                        
                except Exception as e:
                    print(f"❌ Error processing {file_path}: {e}")

    print(f"\n🎉 Finished! GA4 is now live on {updated_count} Texas pages.")

if __name__ == "__main__":
    if not os.path.exists(SITE_ROOT_DIR):
        print(f"Directory not found: {SITE_ROOT_DIR}")
    else:
        print(f"Scanning {SITE_ROOT_DIR} for HTML files...")
        inject_ga4_code(SITE_ROOT_DIR)