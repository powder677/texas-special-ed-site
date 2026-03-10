#!/usr/bin/env python3
"""
Google Analytics Tag Checker and Injector
Checks if pages have the required GA tag and optionally adds it to local files.
"""

import requests
from bs4 import BeautifulSoup
import os
import sys
from urllib.parse import urljoin, urlparse
from typing import Set, List, Dict
import time

# Your Google Analytics tag
GA_TAG_ID = "G-GVLPE273XH"
GA_TAG_HTML = f"""<script async src="https://www.googletagmanager.com/gtag/js?id={GA_TAG_ID}"></script>
<script>
  window.dataLayer = window.dataLayer || [];
  function gtag(){{dataLayer.push(arguments);}}
  gtag('js', new Date());
  gtag('config', '{GA_TAG_ID}');
</script>"""


class GAChecker:
    def __init__(self, base_url=None):
        self.base_url = base_url
        self.visited_urls = set()
        self.results = {
            'has_tag': [],
            'missing_tag': [],
            'errors': []
        }
    
    def has_ga_tag(self, html_content: str) -> bool:
        """Check if HTML content contains the Google Analytics tag"""
        return GA_TAG_ID in html_content
    
    def check_remote_url(self, url: str) -> Dict:
        """Check a single remote URL for GA tag"""
        try:
            response = requests.get(url, timeout=10)
            response.raise_for_status()
            
            has_tag = self.has_ga_tag(response.text)
            
            return {
                'url': url,
                'status': 'has_tag' if has_tag else 'missing_tag',
                'status_code': response.status_code
            }
        except Exception as e:
            return {
                'url': url,
                'status': 'error',
                'error': str(e)
            }
    
    def check_local_file(self, filepath: str) -> Dict:
        """Check a local HTML file for GA tag"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            has_tag = self.has_ga_tag(content)
            
            return {
                'file': filepath,
                'status': 'has_tag' if has_tag else 'missing_tag'
            }
        except Exception as e:
            return {
                'file': filepath,
                'status': 'error',
                'error': str(e)
            }
    
    def add_ga_tag_to_file(self, filepath: str, dry_run=False) -> bool:
        """Add GA tag to a local HTML file (right after <head> tag)"""
        try:
            with open(filepath, 'r', encoding='utf-8') as f:
                content = f.read()
            
            # Check if already has tag
            if self.has_ga_tag(content):
                print(f"✓ {filepath} already has GA tag")
                return False
            
            # Parse and add tag after <head>
            soup = BeautifulSoup(content, 'html.parser')
            head = soup.find('head')
            
            if not head:
                print(f"✗ {filepath} has no <head> tag")
                return False
            
            # Create GA tag elements
            ga_script = BeautifulSoup(GA_TAG_HTML, 'html.parser')
            
            # Insert at beginning of head
            if head.contents:
                head.contents[0].insert_before(ga_script)
            else:
                head.append(ga_script)
            
            if not dry_run:
                with open(filepath, 'w', encoding='utf-8') as f:
                    f.write(str(soup))
                print(f"✓ Added GA tag to {filepath}")
            else:
                print(f"[DRY RUN] Would add GA tag to {filepath}")
            
            return True
        except Exception as e:
            print(f"✗ Error processing {filepath}: {e}")
            return False
    
    def crawl_website(self, start_url: str, max_pages=50) -> List[str]:
        """Crawl a website and return list of URLs (simplified crawler)"""
        to_visit = [start_url]
        visited = set()
        urls = []
        
        domain = urlparse(start_url).netloc
        
        while to_visit and len(visited) < max_pages:
            url = to_visit.pop(0)
            
            if url in visited:
                continue
            
            try:
                response = requests.get(url, timeout=10)
                visited.add(url)
                urls.append(url)
                
                print(f"Crawling: {url}")
                
                soup = BeautifulSoup(response.text, 'html.parser')
                
                # Find all links
                for link in soup.find_all('a', href=True):
                    full_url = urljoin(url, link['href'])
                    parsed = urlparse(full_url)
                    
                    # Only follow links on same domain
                    if parsed.netloc == domain and full_url not in visited:
                        to_visit.append(full_url)
                
                time.sleep(0.5)  # Be polite
                
            except Exception as e:
                print(f"Error crawling {url}: {e}")
        
        return urls
    
    def scan_local_directory(self, directory: str) -> List[str]:
        """Scan directory for HTML files"""
        html_files = []
        for root, dirs, files in os.walk(directory):
            for file in files:
                if file.endswith(('.html', '.htm')):
                    html_files.append(os.path.join(root, file))
        return html_files
    
    def generate_report(self):
        """Generate a summary report"""
        print("\n" + "="*60)
        print("GOOGLE ANALYTICS TAG REPORT")
        print("="*60)
        
        total = len(self.results['has_tag']) + len(self.results['missing_tag'])
        
        print(f"\nTotal pages checked: {total}")
        print(f"✓ Pages with GA tag: {len(self.results['has_tag'])}")
        print(f"✗ Pages missing GA tag: {len(self.results['missing_tag'])}")
        print(f"⚠ Errors: {len(self.results['errors'])}")
        
        if self.results['missing_tag']:
            print("\n--- Pages Missing GA Tag ---")
            for item in self.results['missing_tag']:
                print(f"  • {item}")
        
        if self.results['errors']:
            print("\n--- Errors ---")
            for item in self.results['errors']:
                print(f"  • {item}")
        
        print("="*60 + "\n")


def main():
    print("Google Analytics Tag Checker")
    print("GA Tag ID:", GA_TAG_ID)
    print()
    
    # Choose mode
    print("Choose mode:")
    print("1. Check remote website (crawl and check)")
    print("2. Check list of URLs")
    print("3. Check local HTML files")
    print("4. Add GA tag to local HTML files")
    
    choice = input("\nEnter choice (1-4): ").strip()
    
    checker = GAChecker()
    
    if choice == '1':
        url = input("Enter website URL to crawl: ").strip()
        max_pages = int(input("Max pages to crawl (default 50): ").strip() or "50")
        
        print(f"\nCrawling {url}...")
        urls = checker.crawl_website(url, max_pages)
        
        print(f"\nFound {len(urls)} pages. Checking for GA tags...")
        for url in urls:
            result = checker.check_remote_url(url)
            if result['status'] == 'has_tag':
                checker.results['has_tag'].append(result['url'])
            elif result['status'] == 'missing_tag':
                checker.results['missing_tag'].append(result['url'])
            else:
                checker.results['errors'].append(f"{result['url']}: {result.get('error', 'Unknown error')}")
        
        checker.generate_report()
    
    elif choice == '2':
        print("Enter URLs (one per line, empty line to finish):")
        urls = []
        while True:
            url = input().strip()
            if not url:
                break
            urls.append(url)
        
        for url in urls:
            result = checker.check_remote_url(url)
            if result['status'] == 'has_tag':
                checker.results['has_tag'].append(result['url'])
                print(f"✓ {url}")
            elif result['status'] == 'missing_tag':
                checker.results['missing_tag'].append(result['url'])
                print(f"✗ {url} - MISSING GA TAG")
            else:
                checker.results['errors'].append(f"{result['url']}: {result.get('error', 'Unknown error')}")
                print(f"⚠ {url} - ERROR")
        
        checker.generate_report()
    
    elif choice == '3':
        directory = input("Enter directory path: ").strip()
        
        html_files = checker.scan_local_directory(directory)
        print(f"\nFound {len(html_files)} HTML files")
        
        for filepath in html_files:
            result = checker.check_local_file(filepath)
            if result['status'] == 'has_tag':
                checker.results['has_tag'].append(result['file'])
                print(f"✓ {filepath}")
            elif result['status'] == 'missing_tag':
                checker.results['missing_tag'].append(result['file'])
                print(f"✗ {filepath} - MISSING GA TAG")
            else:
                checker.results['errors'].append(f"{result['file']}: {result.get('error', 'Unknown error')}")
                print(f"⚠ {filepath} - ERROR")
        
        checker.generate_report()
    
    elif choice == '4':
        directory = input("Enter directory path: ").strip()
        dry_run = input("Dry run? (y/n, default=y): ").strip().lower() != 'n'
        
        html_files = checker.scan_local_directory(directory)
        print(f"\nFound {len(html_files)} HTML files")
        
        if dry_run:
            print("\n[DRY RUN MODE - No files will be modified]\n")
        
        added_count = 0
        for filepath in html_files:
            if checker.add_ga_tag_to_file(filepath, dry_run):
                added_count += 1
        
        print(f"\n{'Would add' if dry_run else 'Added'} GA tag to {added_count} files")
    
    else:
        print("Invalid choice")


if __name__ == "__main__":
    main()