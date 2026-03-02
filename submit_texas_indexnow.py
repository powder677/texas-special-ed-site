# File: submit_texas_indexnow.py
import json
import requests
import xml.etree.ElementTree as ET
from urllib.parse import urlparse

# Configuration
api_key = "YOUR_INDEXNOW_API_KEY_HERE"  # Ensure this matches your actual key
sitemap_file = "sitemap.xml"

try:
    tree = ET.parse(sitemap_file)
    root = tree.getroot()
except FileNotFoundError:
    print(f"Error: {sitemap_file} not found.")
    exit()

ns = {'ns': 'http://www.sitemaps.org/schemas/sitemap/0.9'}
raw_urls = []

# Extract all raw URLs first
for url_tag in root.findall('ns:url', ns):
    loc = url_tag.find('ns:loc', ns)
    if loc is not None and loc.text:
        raw_urls.append(loc.text.strip())

if not raw_urls:
    print("No URLs found in sitemap.")
    exit()

# Force the primary host based on the first valid URL
primary_host = urlparse(raw_urls[0]).netloc
primary_scheme = urlparse(raw_urls[0]).scheme
expected_prefix = f"{primary_scheme}://{primary_host}"

clean_url_list = []
rejected_urls = 0

# FILTER: Strictly enforce that every single URL matches the exact host and scheme
for url in raw_urls:
    parsed = urlparse(url)
    if parsed.netloc == primary_host:
        clean_url_list.append(url)
    else:
        rejected_urls += 1

print(f"Target Host: {primary_host}")
print(f"Valid URLs prepared: {len(clean_url_list)}")
if rejected_urls > 0:
    print(f"WARNING: Filtered out {rejected_urls} URLs because they didn't exactly match the host (e.g. missing 'www' or wrong protocol).")

if not clean_url_list:
    exit()

# Build the Payload
key_location = f"{expected_prefix}/{api_key}.txt"

payload = {
    "host": primary_host,
    "key": api_key,
    "keyLocation": key_location,
    "urlList": clean_url_list
}

headers = {
    "Content-Type": "application/json; charset=utf-8"
}

# Fire request
print(f"Verifying Key Location: {key_location}")
print("Firing payload to IndexNow...")

endpoint = "https://api.indexnow.org/indexnow"
response = requests.post(endpoint, data=json.dumps(payload), headers=headers)

if response.status_code == 200:
    print("SUCCESS: 200 OK. URLs successfully submitted and indexed.")
elif response.status_code == 202:
    print("SUCCESS: 202 Accepted. IndexNow is processing it.")
elif response.status_code == 422:
    print("FAILED: 422 Unprocessable Entity.")
    print("REASON: Your API key text file is likely missing, or your server is redirecting the key location URL.")
    print(f"ACTION REQUIRED: Ensure {key_location} loads perfectly in your browser without redirecting.")
else:
    print(f"FAILED: Status Code {response.status_code} - {response.text}")