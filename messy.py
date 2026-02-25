import pandas as pd
from urllib.parse import urlparse, urlunparse
import re

def clean_and_canonicalize_url(url):
    """
    Takes a messy URL and returns the strict, canonicalized version.
    """
    if not isinstance(url, str):
        return url
        
    parsed = urlparse(url)
    
    # 1. Force HTTPS
    scheme = 'https'
    
    # 2. Force www. (if your canonical preference is www)
    netloc = parsed.netloc
    if netloc == 'texasspecialed.com':
        netloc = 'www.texasspecialed.com'
        
    # 3. Clean the path (remove .html, .html.html, and trailing slashes)
    path = parsed.path
    
    # Remove all instances of .html
    path = re.sub(r'\.html+', '', path)
    
    # Remove trailing slash (unless it's the absolute root homepage "/")
    if path != '/' and path.endswith('/'):
        path = path.rstrip('/')
        
    # Reconstruct the URL
    clean_url = urlunparse((scheme, netloc, path, parsed.params, parsed.query, parsed.fragment))
    
    return clean_url

def process_search_console_export(input_csv_path, output_csv_path):
    """
    Reads a Search Console 'Pages.csv', cleans the URLs, and creates a redirect map.
    """
    try:
        # Read the messy URLs from Search Console export
        df = pd.read_csv(input_csv_path)
        
        # Assuming the first column contains the URLs (typically 'Top pages')
        url_column = df.columns[0]
        
        # Create a new column for the Canonical URL
        df['Canonical_URL'] = df[url_column].apply(clean_and_canonicalize_url)
        
        # Determine if a redirect is needed (if the original URL doesn't match the clean one)
        df['Needs_301_Redirect'] = df[url_column] != df['Canonical_URL']
        
        # Filter down to just the ones that need redirects to build a map
        redirect_map = df[df['Needs_301_Redirect']][[url_column, 'Canonical_URL']].copy()
        redirect_map.columns = ['Old_URL', 'New_URL']
        
        # Save the redirect map to a new CSV
        redirect_map.to_csv(output_csv_path, index=False)
        
        print(f"Success! Processed {len(df)} URLs.")
        print(f"Found {len(redirect_map)} URLs that require 301 redirects.")
        print(f"Redirect map saved to: {output_csv_path}")
        
        return redirect_map
        
    except Exception as e:
        print(f"Error processing file: {e}")

# ==========================================
# How to use this script:
# ==========================================
if __name__ == "__main__":
    # 1. Put your Pages.csv from Search Console in the same folder as this script
    input_file = "Pages.csv" 
    
    # 2. This is the file the script will create for you to use in your CMS
    output_file = "301_Redirect_Map.csv"
    
    # 3. Run the function
    # process_search_console_export(input_file, output_file)
    
    # --- Quick Test to show how it works ---
    test_urls = [
        "http://texasspecialed.com/",
        "https://www.texasspecialed.com/districts/plano-isd/evaluation-child-find.html",
        "https://www.texasspecialed.com/districts/north-east-isd/ard-process-guide.html.html",
        "https://texasspecialed.com/districts/frisco-isd/"
    ]
    
    print("Testing the URL Cleaner:\n" + "-"*30)
    for url in test_urls:
        clean = clean_and_canonicalize_url(url)
        print(f"Original: {url}")
        print(f"Cleaned:  {clean}\n")