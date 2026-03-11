import os
import requests
import time
from bs4 import BeautifulSoup
from urllib.parse import urlparse

# --- Configuration ---
SITEMAP_URL = 'https://www.yourstore.com/sitemap.xml' # REPLACE THIS
DOWNLOAD_DIR = './site_html'
REQUEST_DELAY = 0.5  # Seconds to wait between downloads to protect your server
USER_AGENT = 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'

def ensure_dir(directory):
    if not os.path.exists(directory):
        os.makedirs(directory)

def fetch_sitemap_urls(sitemap_url):
    """Fetches and parses the sitemap XML to extract all page URLs."""
    print(f"Fetching sitemap: {sitemap_url}")
    headers = {'User-Agent': USER_AGENT}
    
    try:
        response = requests.get(sitemap_url, headers=headers)
        response.raise_for_status()
    except Exception as e:
        print(f"Failed to fetch sitemap: {e}")
        return []

    # Parse XML
    soup = BeautifulSoup(response.content, 'xml')
    urls = [loc.text for loc in soup.find_all('loc')]
    
    # Filter out obvious non-HTML assets if any slipped into the sitemap
    html_urls = [url for url in urls if not url.endswith(('.pdf', '.jpg', '.png', '.gif', '.mp4'))]
    print(f"Found {len(html_urls)} URLs to process.")
    return html_urls

def download_pages(urls):
    """Downloads the HTML for each URL and saves it locally."""
    ensure_dir(DOWNLOAD_DIR)
    
    headers = {'User-Agent': USER_AGENT}
    success_count = 0

    for i, url in enumerate(urls):
        try:
            # Create a safe filename based on the URL path
            parsed_url = urlparse(url)
            path = parsed_url.path.strip('/')
            if not path:
                filename = 'index.html'
            else:
                # Replace slashes with dashes for a flat directory structure
                filename = path.replace('/', '-') + '.html'
            
            filepath = os.path.join(DOWNLOAD_DIR, filename)

            # Skip if we already downloaded it (allows pausing/resuming)
            if os.path.exists(filepath):
                print(f"[{i+1}/{len(urls)}] Skipping (already exists): {filename}")
                continue

            # Fetch the page
            response = requests.get(url, headers=headers, timeout=10)
            response.raise_for_status()

            # Save to disk
            with open(filepath, 'w', encoding='utf-8') as f:
                f.write(response.text)
            
            print(f"[{i+1}/{len(urls)}] Downloaded: {filename}")
            success_count += 1
            
            # Rate limit to protect the server
            time.sleep(REQUEST_DELAY)

        except Exception as e:
            print(f"[{i+1}/{len(urls)}] Error downloading {url}: {e}")

    print("\n--- Download Complete ---")
    print(f"Successfully downloaded {success_count} new pages.")

def run_downloader():
    if SITEMAP_URL == 'https://www.yourstore.com/sitemap.xml':
        print("ERROR: Please update the SITEMAP_URL variable with your actual sitemap.")
        return
        
    urls = fetch_sitemap_urls(SITEMAP_URL)
    if urls:
        download_pages(urls)

if __name__ == "__main__":
    # Note: Requires 'requests' and 'lxml' libraries
    # pip install requests beautifulsoup4 lxml
    run_downloader()