import requests
from bs4 import BeautifulSoup
from urllib.parse import urljoin, urlparse, urldefrag
import pandas as pd
import time

domain = "https://www.texasspecialed.com"
# Extract just the domain name (www.texasspecialed.com) for accurate internal link checking
target_netloc = urlparse(domain).netloc 

visited = set()
to_visit = [domain]

broken_links = []
internal_links = []

# Using a standard browser User-Agent prevents websites from blocking the script
headers = {
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36'
}

while to_visit:
    url = to_visit.pop()

    # Remove URL fragments (e.g., changing /page#section1 to /page) to avoid crawling the same page twice
    url, _ = urldefrag(url)

    if url in visited:
        continue

    visited.add(url)
    print("Crawling:", url)

    try:
        r = requests.get(url, headers=headers, timeout=10)
        status = r.status_code
    except requests.exceptions.RequestException as e:
        # Catching specific request errors gives you more descriptive logs in your CSV
        broken_links.append((url, f"connection_error: {type(e).__name__}"))
        continue

    if status >= 400:
        broken_links.append((url, status))
        continue

    # Only parse the page if it is actually HTML (skips trying to parse PDFs, images, etc.)
    content_type = r.headers.get('Content-Type', '').lower()
    if 'text/html' not in content_type:
        continue

    soup = BeautifulSoup(r.text, "html.parser")

    for link in soup.find_all("a", href=True):
        raw_href = link["href"]
        
        # Ignore non-webpage links that crash the requests library
        if raw_href.startswith(('mailto:', 'tel:', 'javascript:')):
            continue

        full = urljoin(url, raw_href)
        full, _ = urldefrag(full) 
        parsed = urlparse(full)

        # Check if the network location (domain) matches our target exactly
        if parsed.netloc == target_netloc:
            internal_links.append((url, full))

            if full not in visited:
                to_visit.append(full)

    # Be polite to the server
    time.sleep(0.5)

# Save results
df_broken = pd.DataFrame(broken_links, columns=["URL", "Status"])
df_links = pd.DataFrame(internal_links, columns=["Source Page", "Link"])

df_broken.to_csv("broken_pages.csv", index=False)
df_links.to_csv("internal_links.csv", index=False)

print("\n--- Crawl complete ---")
print(f"Broken pages found: {len(df_broken)}")
print(f"Internal links mapped: {len(df_links)}")