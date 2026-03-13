import os
import requests
from bs4 import BeautifulSoup
from urllib.parse import urlparse

# --- CONFIGURATION ---
# Set this to the root folder of your website. 
# "." means the current folder where the script is running.
ROOT_DIR = "."  

broken_links = []

def check_external_url(url):
    """Pings an external URL to see if it is alive."""
    try:
        # Use a standard User-Agent so websites don't block our script as a basic bot
        headers = {'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64)'}
        
        # We use HEAD first because it's faster (doesn't download the whole page)
        response = requests.head(url, headers=headers, allow_redirects=True, timeout=5)
        
        if response.status_code >= 400:
            # Some servers reject HEAD requests. If it fails, try a standard GET request.
            response = requests.get(url, headers=headers, stream=True, timeout=5)
            if response.status_code >= 400:
                return False, f"HTTP {response.status_code}"
                
        return True, "OK"
    except requests.RequestException as e:
        return False, "Connection Error/Timeout"

def check_local_file(base_path, current_file_path, href):
    """Checks if a local file actually exists on the hard drive."""
    # Strip off anchor links or query parameters (e.g., index.html#section-1)
    clean_href = href.split('#')[0].split('?')[0]
    
    if not clean_href: 
        return True, "Anchor only" # It was just an anchor e.g., href="#"

    if clean_href.startswith('/'):
        # It's a root-relative path (e.g., /districts/index.html)
        # We strip the leading slash and join it to the project root
        target_path = os.path.join(base_path, clean_href.lstrip('/'))
    else:
        # It's a document-relative path (e.g., ../index.html or style.css)
        current_dir = os.path.dirname(current_file_path)
        target_path = os.path.normpath(os.path.join(current_dir, clean_href))

    if os.path.exists(target_path) and os.path.isfile(target_path):
        return True, "File Exists"
    else:
        return False, "File Not Found Locally"

def scan_directory(directory):
    """Walks through all folders and finds HTML files."""
    for root, _, files in os.walk(directory):
        for file in files:
            if file.endswith('.html'):
                file_path = os.path.join(root, file)
                check_links_in_file(file_path)

def check_links_in_file(file_path):
    """Parses an HTML file and tests all its links."""
    print(f"Scanning: {file_path}")
    
    with open(file_path, 'r', encoding='utf-8') as f:
        try:
            soup = BeautifulSoup(f, 'lxml')
        except Exception as e:
            print(f"  [!] Error parsing HTML: {e}")
            return

    links = soup.find_all('a', href=True)
    
    for link in links:
        href = link['href'].strip()
        
        # Skip emails, phone numbers, and javascript triggers
        if href.startswith(('mailto:', 'tel:', 'javascript:')) or not href:
            continue
            
        parsed_url = urlparse(href)
        
        # Route to the correct checker based on link type
        if parsed_url.scheme in ('http', 'https'):
            is_valid, status = check_external_url(href)
            link_type = "External"
        else:
            is_valid, status = check_local_file(ROOT_DIR, file_path, href)
            link_type = "Internal"
            
        if not is_valid:
            broken_links.append({
                'file': file_path,
                'href': href,
                'type': link_type,
                'error': status
            })

if __name__ == "__main__":
    print("Starting broken link checker... This may take a minute if you have a lot of external links.")
    print("-" * 50)
    
    scan_directory(ROOT_DIR)
    
    print("\n" + "="*50)
    print("SCAN COMPLETE")
    print("="*50)
    
    if not broken_links:
        print("✅ Awesome job! No broken links found.")
    else:
        print(f"❌ Found {len(broken_links)} broken link(s):\n")
        for bl in broken_links:
            print(f"📄 File:   {bl['file']}")
            print(f"🔗 Link:   {bl['href']} ({bl['type']})")
            print(f"⚠️  Error:  {bl['error']}")
            print("-" * 40)